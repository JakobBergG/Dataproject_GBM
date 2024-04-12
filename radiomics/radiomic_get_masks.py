import SimpleITK as sitk
import os
import csv
import json

ONLY_USE_LARGEST_LESION = True

def filter_mask(mask_path, brain_mask_path, output_path):
    gtv_mask = sitk.ReadImage(mask_path)
    if ONLY_USE_LARGEST_LESION:
        gtv_mask = get_largest_lesion(gtv_mask)

    # DILATION - In paper: 2 cm
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelType(sitk.sitkBall)
    radius = 20 # in mm. DICOM standard
    dilate_filter.SetKernelRadius((radius, radius, radius // 2)) # Due to OUR sampling of images 1, 1, .5
    dilate_filter.SetForegroundValue(1)

    new_mask = dilate_filter.Execute(gtv_mask)

    # SKULL AS DILATION BOUNDARY - Make sure the dilation doesn't cross the skull
    and_filter = sitk.AndImageFilter()
    brain_mask = sitk.ReadImage(brain_mask_path)

    new_mask = and_filter.Execute(new_mask, brain_mask)

    # REMOVE GTV AREA - We seek to extract features from the RING around the GTV.
    subtract_filter = sitk.SubtractImageFilter()

    new_mask = subtract_filter.Execute(new_mask, gtv_mask)

    # SAVE NEW MASK
    sitk.WriteImage(new_mask, output_path)

def get_largest_lesion(mask):
    '''Returns the largest lesion
    '''
    component_image = sitk.ConnectedComponent(mask)
    sorted_component_image = sitk.RelabelComponent(component_image, sortByObjectSize=True)
    largest_component_binary_image = sorted_component_image == 1

    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(largest_component_binary_image)
    print("Found largest lesion with size:", stats.GetNumberOfPixels(1))
    return largest_component_binary_image

with open("D:\\GBM\\output_test\\radiomic_results\\available_patients.json", "r") as f:
    available_patients = json.load(f)

for patient_id in available_patients:
    output_path = f"D:\\GBM\\output_test\\radiomic_results\\masks\\masks_test\\{patient_id}"

    print("Now running for:", patient_id)
    try:
        os.mkdir(output_path)
    except OSError:
        print("Folder already existed", patient_id)

    mask_folderpath = f"D:\\GBM\\summary\\AUH\\{patient_id}"
    for filename in os.listdir(mask_folderpath):
        if filename.startswith("time2") and filename.endswith("gtv.nii.gz"):
            time2 = filename.split("_")[2]
        
    
    mask_filepath = f"D:\\GBM\\summary\\AUH\\{patient_id}\\time2_{patient_id}_{time2}_gtv.nii.gz"
    brain_mask_path = f"D:\\GBM\\output\\AUH\\{patient_id}\\brain_mr\\output_brains\\{patient_id}_{time2}_MR_mask_cleaned.nii"
    output_filepath = output_path + f"\\{patient_id}_{time2}_feature_mask.nii.gz"
    try:
        filter_mask(mask_filepath, brain_mask_path, output_filepath)
    except Exception as e:
        print("Error happened:\n", e, "\nRemoving created directory.")
        os.rmdir(output_path)
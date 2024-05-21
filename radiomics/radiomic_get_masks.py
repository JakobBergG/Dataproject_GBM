import SimpleITK as sitk
import os
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


with open("D:\\GBM\\radiomic_results\\available_patients.json", "r") as f:
    available_patients = json.load(f)

hospitals = ["AUH", "OUH", "CUH"]
for hospital in hospitals:
    patients = os.listdir(f"D:\\GBM\\nii_prepared\\{hospital}")

    for patient_id in patients:
        if patient_id not in available_patients:
            continue
        output_path = f"D:\\GBM\\radiomic_results\\masks\\time2\\{patient_id}"

        # Create directory for patient
        print(output_path)
        print("Now running for:", patient_id)
        try:
            os.mkdir(output_path)
        except OSError:
            print("Folder already existed", patient_id)

        
        # Find date of scans
        for filename in os.listdir(f"D:\\GBM\\nii_prepared\\{hospital}\\{patient_id}"):
            

        # Define paths to masks
        mask_filepath = MASK_GTV.format(hospital = hospital, patient_id = patient_id)
        brain_mask_path = MASK_BRAIN.format(hospital = hospital, patient_id = patient_id)
        output_filepath = output_path + f"\\{patient_id}_MASK_RING.nii.gz"

        try:
            filter_mask(mask_filepath, brain_mask_path, output_filepath)
        except Exception as e:
            print("Error happened:\n", e, "\nRemoving created directory.")
            os.rmdir(output_path)
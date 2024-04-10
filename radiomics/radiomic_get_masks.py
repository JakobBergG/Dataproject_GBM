import SimpleITK as sitk
import os
import csv
import json

def filter_mask(mask_path, brain_mask_path, output_path):
    gtv_mask = sitk.ReadImage(mask_path)

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

with open("D:\\GBM\\output_test\\radiomic_results\\available_patients.json", "r") as f:
    available_patients = json.load(f)

for patient_id in available_patients:
    patient_dir = f"D:\\GBM\\output_test\\radiomic_results\\new_masks\\{patient_id}"

    print("Now running for:", patient_id)
    try:
        os.mkdir(patient_dir)
    except OSError:
        print("Folder already existed", patient_id)

    mask_path = f"D:\\GBM\output\\AUH\\{patient_id}\\predicted_gtvs\\"
    time0 = min(os.listdir(mask_path)).split("_")[1] # Format is 0114_20140723_gtv.nii.gz
    
    mask_path = f"D:\\GBM\output\\AUH\\{patient_id}\\predicted_gtvs\\{patient_id}_{time0}_gtv.nii"
    brain_mask_path = f"D:\\GBM\\output\\AUH\\{patient_id}\\brain_mr\\output_brains\\{patient_id}_{time0}_MR_mask_cleaned.nii"
    output_path = f"D:\\GBM\\output_test\\radiomic_results\\new_masks\\{patient_id}\\{patient_id}_{time0}_feature_mask.nii.gz"
    try:
        filter_mask(mask_path, brain_mask_path, output_path)
    except Exception as e:
        print(e, "Removing created directory.")
        os.rmdir(patient_dir)
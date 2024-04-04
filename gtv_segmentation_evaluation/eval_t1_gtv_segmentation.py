import os
import SimpleITK as sitk
import re
import math
import medpy.metric
import numpy as np
import json

def msd(ct_mask : sitk.Image, mr_mask : sitk.Image) -> float:
    '''Calculate Mean Surface Distance between mr and ct brain masks.
    Returns float MSD(ct_mask, mr_mask)'''
    spacing = ct_mask.GetSpacing()
    mr_mask = reslice_image(mr_mask, ct_mask, is_label=True)
    mr_mask_array = sitk.GetArrayFromImage(mr_mask)
    ct_mask_array = sitk.GetArrayFromImage(ct_mask)
    mean_surface_distance = medpy.metric.binary.assd(mr_mask_array, ct_mask_array, voxelspacing=spacing)
    
    return mean_surface_distance


def reslice_image(itk_image : sitk.Image, itk_ref : sitk.Image , is_label : bool = False) -> sitk.Image:
    '''Reslice one image to the grid of another image (when they are registered)'''
    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(itk_ref)
    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)
    

def get_hd(baseline : sitk.Image,rec : sitk.Image) -> tuple:
    '''Get hausdorff distance between tumor area at baseline and tumor area at recurrence
    Returns tuple (hd, hd95)'''
    rec = reslice_image(rec, baseline, is_label=True)
    baseline_array = sitk.GetArrayFromImage(baseline)
    rec_array = sitk.GetArrayFromImage(rec)
    hd = medpy.metric.binary.hd(baseline_array, rec_array)
    hd95 = medpy.metric.binary.hd95(baseline_array ,rec_array )
    
    return hd, hd95
    

def evaluate(hospital):
        
    # Evaluation of the segmentation of gtvs for a hospital (AUH, CUH, OUH)
    # Only patients with the file "gtv.nii.gz" in RTSTRUCTS_0
    # is used in the evaluation.

    metrics = {}

    prediction_folder_path = f"D:\\GBM\\output\\{hospital}"
    gt_folder_path = f"D:\\GBM\\nii\\{hospital}"

    prediction_folders = [f.path for f in os.scandir(prediction_folder_path) if f.is_dir()]

    for prediction_folder in prediction_folders:
        print(f"running on patient_folder {os.path.basename(prediction_folder)}")
        patient_number = os.path.basename(prediction_folder)

        # get prediction file
        prediction_path = os.path.join(prediction_folder, "MR_to_CT_gtv")
        
        try:
            prediction_filelist = [f.path for f in os.scandir(prediction_path)]
        except:
            print(f"could not find {prediction_folder}")
            continue
        prediction_file = min(prediction_filelist)
        

        # get gt file
        gt_path = os.path.join(gt_folder_path, patient_number)
        gt_path = [f.path for f in os.scandir(gt_path) if f.is_dir() and f.path.endswith("_CT")][0]
        gt_path = os.path.join(gt_path, "RTSTRUCTS_0")
        try:
            gt_files = [f.path for f in os.scandir(gt_path)]
            gt_file = [f for f in gt_files if os.path.basename(f) == "gtv.nii.gz"][0]
        except:
            print(f"could not get gt_files or gt_file in {gt_path}")
            continue


        # read files
        prediction = sitk.ReadImage(prediction_file)
        gt = sitk.ReadImage(gt_file)

        try:
            msd_result = msd(prediction, gt)
            hd_result, hd95_result = get_hd(prediction, gt)
        except Exception as e:
            print(f"could not compute metrics: {e}")
            continue

        metrics[patient_number] = {"msd": msd_result, "hd": hd_result, "hd95": hd95_result}


        with open(f"{hospital}_metrics.json", "w") as outfile:
            json.dump(metrics, outfile)


evaluate("OUH")
    

 

"""

# Evaluation of AUH
# Only patients with the file "gtv.nii.gz" in RTSTRUCTS_0
# is used in the evaluation.

AUH_metrics = {}

prediction_folder_path = "D:\\GBM\\output\\AUH"
gt_folder_path = "D:\\GBM\\nii\\AUH"

prediction_folders = [f.path for f in os.scandir(prediction_folder_path) if f.is_dir()]

for prediction_folder in prediction_folders:
    print(f"running on patient_folder {os.path.basename(prediction_folder)}")
    patient_number = os.path.basename(prediction_folder)

    # get prediction file
    prediction_path = os.path.join(prediction_folder, "MR_to_CT_gtv")
    
    try:
        prediction_filelist = [f.path for f in os.scandir(prediction_path)]
    except:
        print(f"could not find {prediction_folder}")
        continue
    prediction_file = min(prediction_filelist)
    

    # get gt file
    gt_path = os.path.join(gt_folder_path, patient_number)
    gt_path = [f.path for f in os.scandir(gt_path) if f.is_dir() and f.path.endswith("_CT")][0]
    gt_path = os.path.join(gt_path, "RTSTRUCTS_0")
    try:
        gt_files = [f.path for f in os.scandir(gt_path)]
        gt_file = [f for f in gt_files if os.path.basename(f) == "gtv.nii.gz"][0]
    except:
        print(f"could not get gt_files or gt_file in {gt_path}")
        continue


    # read files
    prediction = sitk.ReadImage(prediction_file)
    gt = sitk.ReadImage(gt_file)

    try:
        msd_result = msd(prediction, gt)
        hd_result, hd95_result = get_hd(prediction, gt)
    except Exception as e:
        print(f"could not compute metrics: {e}")
        continue

    AUH_metrics[patient_number] = {"msd": msd_result, "hd": hd_result, "hd95": hd95_result}


with open("AUH_metrics.json", "w") as outfile:
    json.dump(AUH_metrics, outfile)


"""
    






    


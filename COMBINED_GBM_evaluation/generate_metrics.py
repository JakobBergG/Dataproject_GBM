import os
import SimpleITK as sitk
import re
import shutil
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

labels_path = "E:/Jasper/nnUNet/nnUNet_raw_data/Task805_COMBINED_GBM/labelsTs"
predictions_path = "D:/GBM/COMBINED_GBM_predictions/Task806_ANOUK_GBM"
metrics = {}

prediction_files = [f.path for f in os.scandir(predictions_path) if f.path.endswith("nii.gz")]
labels_files = [f.path for f in os.scandir(labels_path) if f.path.endswith("nii.gz")]
for prediction in prediction_files:
    # find the label
    try:
        label = [f for f in labels_files if f.endswith(os.path.basename(prediction))][0]
    except Exception as e:
        print(f"could not get label for file {prediction}. Error: {e}")
        continue

    # get the key for the file:
    key = re.sub(".nii.gz", "", os.path.basename(prediction))

    try:
        print(f"reading images: {prediction}")
        prediction = sitk.ReadImage(prediction)
        label = sitk.ReadImage(label)

        print(f"calculating metrics...")
        msd_result = msd(prediction, label)
        hd_result, hd95_result = get_hd(prediction, label)

        metrics[key] = {"msd": msd_result, "hd": hd_result, "hd95": hd95_result}

        file_name = "Task805_ANOUK_GBM_metrics.json"
        print(f"saving metrics as {file_name}")
        with open(f"{file_name}", "w") as outfile:
                json.dump(metrics, outfile)

    except Exception as e:
        print(f"Error in calculating metrics for key: {prediction}. Error: {e}")

import os
import SimpleITK as sitk
import re
import shutil
import math
import medpy.metric
import numpy as np
import json

# Note this file is not build the same way as the eval_t1_gtv_segmentation.py

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
    


hospitals = ["AUH", "OUH", "CUH"]
label_base_path = "D:\\GBM\\nii"
predictions_base_path = "D:\GBM\output"
for hospital in hospitals:
    metrics = {}
    label_folders_path = os.path.join(label_base_path, hospital)
    # get list of label folders
    label_folders = [f.path for f in os.scandir(label_folders_path) if f.is_dir()]
    # work on one patient at a time
    for label_folder in label_folders:
        patient_number = os.path.basename(label_folder)

        # see if label exists
        try:
            ct_path = [f.path for f in os.scandir(label_folder) if f.path.endswith("CT")][0]
            label_path = [f.path for f in os.scandir(os.path.join(ct_path, "RTSTRUCTS_0")) if os.path.basename(f) == "gtv.nii.gz"][0]

        except Exception as e:
            print(f"could not get label for patient {patient_number}: {e}")
            continue
    
        # now we are left with an existing label for the patient.
        # now search for patient in the output folder (training input)

        # get the predicted gtv
        try:
            # first determine the time2 MR file by searching in the summary file
            t2_files_path = f"D:\\GBM\\summary\\{hospital}\\{patient_number}"
            # if t2_file_path cant be found this will give an error since there will be an empty list
            t2_file_path = [f.path for f in os.scandir(t2_files_path) if os.path.basename(f.path).startswith("time2") and f.path.endswith("MR.nii.gz")][0]
            # now retrieve the t2 file to search for in the output folder
            prediction_file_name = re.sub("time2_", "", os.path.basename(t2_file_path))
            prediction_file_name = re.sub("MR.nii.gz", "gtv.nii.gz", prediction_file_name)
            print(f"prediction_file_name: {prediction_file_name}")

            prediction_files_path = os.path.join(predictions_base_path, hospital, patient_number, "MR_to_CT_gtv")
            prediction_file = [f.path for f in os.scandir(prediction_files_path) if os.path.basename(f.path) == prediction_file_name][0]
        except Exception as e:
            print(f"could not get prediction file for patient {patient_number}: {e}")
            continue
        
        # We now have the paths for the predicted gtv and the clinical deliniation
        # load images and compute metrics

        try:
            print(f"Computing metrics for patient: {patient_number}")

            # read files
            prediction = sitk.ReadImage(prediction_file)
            gt = sitk.ReadImage(label_path)

            # compute metrics
            msd_result = msd(prediction, gt)
            hd_result, hd95_result = get_hd(prediction, gt)

            # save metrics in list
            metrics[patient_number] = {"msd": msd_result, "hd": hd_result, "hd95": hd95_result}

            # save metrics as json
            with open(f"{hospital}_metrics_t2.json", "w") as outfile:
                json.dump(metrics, outfile)
        except Exception as e:
            print(f"failed computing metrics for patient: {patient_number}: {e}")



        




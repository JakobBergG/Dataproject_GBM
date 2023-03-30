import os
import SimpleITK as sitk
import numpy as np
import medpy.metric
import json
import utils

SAVE_AS_JSON = True

def msd(Image1 : sitk.Image,Image2 : sitk.Image) -> float:
    '''Calculate Mean Surface Distance between two images.
    Returns float MSD(Image1, Image2)'''
    Image2 = utils.reslice_image(Image1, Image2, is_label=True)
    Image1_array = sitk.GetArrayFromImage(Image1)
    Image2_array = sitk.GetArrayFromImage(Image2)
    mean_surface_distance = medpy.metric.binary.asd(Image1_array, Image2_array)
    
    return mean_surface_distance

basepath = utils.get_path("path_data")
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]

patient_dic = {}

for patient in patientfolders:
    patient_id = os.path.basename(patient)

    # Find CT brain file
    ct_mask_path = os.path.join(patient, utils.get_path('local_path_brainmask_ct'))
    ct_mask_filelist = [ f.path for f in os.scandir(ct_mask_path) if f.is_file() ]
    ct_mask = ''
    for pathstr in ct_mask_filelist:
        if os.path.basename(pathstr).endswith('mask.nii.gz'): # FIX NAME !!!!!!!
            ct_mask = pathstr
    
    # Skip patient if there is no CT brain file
    if ct_mask == '':
        print(f"no ct brain file for {patient_id}")
        continue

    # Find registered MR brain file
    mr_mask_path = os.path.join(patient, utils.get_path('MR_to_CT_mask'))   # FIX NAME !!!!!!!
    mr_mask_filelist = [ f.path for f in os.scandir(mr_mask_path) if f.is_file() ]
    mr_masks = []
    for pathstr in mr_mask_filelist:
        if os.path.basename(pathstr).endswith('mask.nii.gz'): # FIX NAME !!!!!!!
            mr_masks.append(pathstr)

    # Make a list with Mean Surface Distances for each patient
    patient_dic[patient_id] = []
    
    ct_mask = sitk.ReadImage(ct_mask)

    for mr_mask in mr_masks:
        # For each mr mask compute Mean Surface Difference with ct mask
        mr_mask = sitk.ReadImage(mr_mask)
        patient_dic[patient_id].append(msd(ct_mask, mr_mask))
    
    # Append the average value of all MSDs for the patient at the end of list
    avg_msd = np.mean(patient_dic[patient_id])
    patient_dic[patient_id].append(avg_msd)

# Sort patient dictionary by average MSD
sorted_patients = sorted(patient_dic.items, key = lambda L: L[1][-1])
patient_dic = {key : value for key, value in sorted_patients}

if SAVE_AS_JSON:
    with open(os.path.join(utils.get_path("path_output"), "registration_mask_MSD.json") , "w", encoding="utf-8") as f:
        json.dump(patient_dic, f, ensure_ascii=False, indent = 4)
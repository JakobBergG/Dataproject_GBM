import os
import SimpleITK as sitk
import numpy as np
import json
import common.utils as utils
import common.metrics as metrics
import logging

log = logging.getLogger(__name__)

output_path = ''

def add_msd_to_json(patient_folder : str):

    patient_id = os.path.basename(patient_folder)

    json_filename = os.path.basename(output_path)
    if os.path.isfile(output_path):
        with open(output_path, "r") as f:
            patient_dic : dict = json.load(f)
    else:
        patient_dic = {}
    
    # Find CT brain file
    ct_mask_path = os.path.join(patient_folder, utils.get_path('local_path_brainmasks_ct'))
    ct_mask_filelist = [ f.path for f in os.scandir(ct_mask_path) if f.is_file() ]
    ct_mask = ''
    for pathstr in ct_mask_filelist:
        if os.path.basename(pathstr).endswith('mask_cleaned.nii.gz'):
            ct_mask = pathstr

    if ct_mask == '':
        log.error(f"No CT file for patient {patient_id}")
        raise Exception(f"No CT file for patient {patient_id}")
    
    # Find registered MR brain file
    mr_mask_path = os.path.join(patient_folder, utils.get_path('local_path_moved_mr')) 
    mr_mask_filelist = [ f.path for f in os.scandir(mr_mask_path) if f.is_file() ]
    mr_masks = []
    for pathstr in mr_mask_filelist:
        if os.path.basename(pathstr).endswith('mask.nii.gz'):
            mr_masks.append(pathstr)
    
    # Make a list with Mean Surface Distances for the patient
    patient_dic[patient_id] = []
    
    ct_mask = sitk.ReadImage(ct_mask)

    for mr_mask in mr_masks:
        # For each mr mask compute Mean Surface Distance to ct mask
        mr_mask = sitk.ReadImage(mr_mask)
        patient_dic[patient_id].append(metrics.msd(ct_mask, mr_mask))
    
    # Append the average value of all MSDs for the patient at the end of list
    avg_msd = np.mean(patient_dic[patient_id])
    patient_dic[patient_id].append(avg_msd)

    # Sort patient dictionary by average MSD
    sorted_patients = sorted(patient_dic.items(), key = lambda L: L[1][-1])
    patient_dic = {key : value for key, value in sorted_patients}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patient_dic, f, ensure_ascii=False, indent = 4)
    
    log.info(f"Succesfully added MSDs for {patient_id} to {json_filename}.")

def setup(output_name : str):
    '''
    Setup path for output
    '''
    global output_path
    output_path = os.path.join(utils.get_path("path_output"), output_name)
import os
import SimpleITK as sitk
import numpy as np
import json
import common.utils as utils
import common.metrics as metrics
import logging
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)

def add_msd_to_json(patient_folder : str, output_name : str):
    '''
    Calculates Mean Surface Distance between MR and CT mask for each MR mask and
    adds the MSDs and their average value to dictionary in JSON file.
    If JSON file does not exist, it creates a new dictionary and a new JSON file.
    '''

    output_path = os.path.join(utils.get_path("path_output"), output_name)
    patient_id = os.path.basename(patient_folder)
    output_patient_folder = utils.get_output_patient_path(patient_id)

    json_filename = os.path.basename(output_path)
    if os.path.isfile(output_path):
        with open(output_path, "r") as f:
            patient_dic : dict = json.load(f)
    else:
        patient_dic = {}
    
    # Find CT brain file
    ct_mask_path = os.path.join(output_patient_folder, utils.get_path('local_path_brainmasks_ct'))
    ct_mask_filelist = [ f.path for f in os.scandir(ct_mask_path) if f.is_file() ]
    ct_mask = ''
    for pathstr in ct_mask_filelist:
        if os.path.basename(pathstr).endswith('mask_cleaned.nii.gz'):
            ct_mask = pathstr

    if ct_mask == '':
        log.error(f"No CT file for patient {patient_id}")
        raise Exception(f"No CT file for patient {patient_id}")
    
    # Find registered MR brain file
    mr_mask_path = os.path.join(output_patient_folder, utils.get_path('local_path_moved_mr')) 
    mr_mask_filelist = [ f.path for f in os.scandir(mr_mask_path) if f.is_file() ]
    mr_masks = []
    for pathstr in mr_mask_filelist:
        if os.path.basename(pathstr).endswith('mask.nii.gz'):
            mr_masks.append(pathstr)
    
    # Make a list with Mean Surface Distances for the patient
    patient_dic[patient_id] = []
    
    ct_mask = sitk.ReadImage(ct_mask)

    for mr_mask in mr_masks:
        # For each MR mask compute Mean Surface Distance to CT mask
        mr_mask = sitk.ReadImage(mr_mask)
        patient_dic[patient_id].append(metrics.msd(ct_mask, mr_mask))
    
    # Append the average value of all MSDs for the patient at the end of list
    avg_msd = np.mean(patient_dic[patient_id])
    patient_dic[patient_id].append(avg_msd)

    # Save the new/updated dictionary
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patient_dic, f, ensure_ascii=False, indent = 4)
    
    log.info(f"Succesfully added MSDs for {patient_id} to {json_filename}.")


def sort_msd_dict(output_name : str):
    '''
    Sort the patients in the dictionary by avg MSD value
    '''
    output_path = os.path.join(utils.get_path("path_output"), output_name)
    with open(output_path, "r") as f:
        patient_dic : dict = json.load(f)

    # Sort patient dictionary by average MSD
    sorted_patients = sorted(patient_dic.items(), key = lambda L: L[1][-1])
    patient_dic = {key : value for key, value in sorted_patients}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patient_dic, f, ensure_ascii=False, indent = 4)


def msd_histogram(json_filename : str, output_name: str):
    '''
    Plots a histogram of the MSD scores from the registration
    '''

    # Load dictionary from JSON file
    json_path = os.path.join(utils.get_path("path_output"), json_filename)
    with open(json_path, "r") as f:
        patient_dic : dict = json.load(f)
    
    # Get a list of MSD score for each registration, values[-1] is the average value for the patient
    scores = [msd for patient, values in patient_dic.items() for msd in values[:-1]]

    # Plot histogram and save
    plt.hist(scores, bins=100)
    plt.title("Histogram of MSD values for registrations")
    plt.xlabel("MSD score")
    plt.ylabel("Count")

    output_path = os.path.join(utils.get_path("path_output"), output_name)
    plt.savefig(output_path)
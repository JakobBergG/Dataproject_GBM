import os
import common.utils as utils
from common.prediction import run_prediction
import logging

log = logging.getLogger(__name__)

basepath = utils.get_path("path_data")

local_path_brain_ct = utils.get_path("local_path_brain_ct")
local_path_brain_mr = utils.get_path("local_path_brain_mr")
local_path_brainmasks_ct = utils.get_path("local_path_brainmasks_ct")
local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")

def run_brainmask_predictions(patient_folder : str, nnUNet_ct_task_id : int, nnUNet_mr_task_id : int):
    patient_id = os.path.basename(patient_folder)
    output_patient_folder = utils.get_output_patient_path(patient_id)

    # CT predictions:
    
    # start off by creating a lot of folders
    # create brain_ct folder if not exists
    brain_ct_folder = os.path.join(output_patient_folder, local_path_brain_ct)
    if not os.path.exists(brain_ct_folder):
        os.mkdir(brain_ct_folder)
    # create nnUNet input folder if not exists
    nnUNet_input_folder = os.path.join(brain_ct_folder, "nnUNet_input")
    if not os.path.exists(nnUNet_input_folder):
        os.mkdir(nnUNet_input_folder)
    #create output folder if not exists
    output_dest = os.path.join(output_patient_folder, local_path_brainmasks_ct)
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)

    # now ready to run prediction
    log.info(f"Running CT brain mask prediction for {patient_id}")
    scans_ending = "_CT_res.nii.gz"
    nnUNet_ending = "_CT_res_mask_0000.nii.gz"

    run_prediction(patient_folder, scans_ending, nnUNet_input_folder,
                   nnUNet_ending, nnUNet_ct_task_id, output_dest)
    
    # MR predictions:
    
    # start off by creating a lot of folders
    # create brain_mr folder if not exists
    brain_mr_folder = os.path.join(output_patient_folder, local_path_brain_mr)
    if not os.path.exists(brain_mr_folder):
        os.mkdir(brain_mr_folder)
    # create nnUNet input folder if not exists
    nnUNet_input_folder = os.path.join(brain_mr_folder, "nnUNet_input")
    if not os.path.exists(nnUNet_input_folder):
        os.mkdir(nnUNet_input_folder)
    #create output folder if not exists¨
    output_dest = os.path.join(output_patient_folder, local_path_brainmasks_mr)
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)

    # now ready to run prediction
    log.info(f"Running MR brain mask prediction for {patient_id}")
    scans_ending = "_MR_res.nii.gz"
    nnUNet_ending = "_MR_res_mask_0000.nii.gz"

    run_prediction(patient_folder, scans_ending, nnUNet_input_folder,
                   nnUNet_ending, nnUNet_mr_task_id, output_dest)
    
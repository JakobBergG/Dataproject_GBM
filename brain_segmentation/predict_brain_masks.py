import os
import common.utils as utils
import argparse
import shutil
import re
from common.run_prediction import nnUNet_predict
import logging

log = logging.getLogger(__name__)

# task ids used by nnUNet -- these are default values and can be changed
# when running setup_prediction
ct_task_id = 800
mr_task_id = 801

basepath = utils.get_path("path_data")

local_path_brain_ct = utils.get_path("local_path_brain_ct")
local_path_brain_mr = utils.get_path("local_path_brain_mr")

def setup_prediction(nnUNet_ct_task_id : int, nnUNet_mr_task_id : int):
    '''
    Setup stuff required for nnUNet to run properly
    '''
    global ct_task_id
    global mr_task_id
    # setup GPU 
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    ct_task_id = nnUNet_ct_task_id
    mr_task_id = nnUNet_mr_task_id


def move_mr_scans(patient_folder : str, destination_folder : str):
    '''
    Move the MR scans in patientfolder to destination_folder which nnUNet
      can use as input
    '''
    # find MR_res scans
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    mr_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith("_MR_res.nii.gz"):
            mr_list.append(file)

    # now copy files, also changing name to comply with nnunet input requirements
    for source in mr_list:
        oldname = os.path.basename(source)
        newname = re.sub("_MR_res", "_MR_res_mask_0000", oldname)
        dest = os.path.join(destination_folder, newname)
        shutil.copy2(source, dest)


def move_ct_scans(patient_folder : str, destination_folder : str):
    '''
    Move the MR scans in patientfolder to destination_folder which nnUNet
      can use as input
    '''
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    ct_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith("_CT_res.nii.gz"):
            ct_list.append(file)

    # now copy files, also changing name to comply with nnunet input requirements
    for source in ct_list:
        oldname = os.path.basename(source)
        newname = re.sub("_CT_res", "_CT_res_mask_0000", oldname)
        dest = os.path.join(destination_folder, newname)
        shutil.copy2(source, dest)


patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]

def run_mr_prediction(patient_folder : str):
    patient_id = os.path.basename(patient_folder)
    # start by moving scans
    log.info(f"Copying MR scans for patient {patient_id}")
    brain_folder = os.path.join(patient_folder, local_path_brain_mr)
    # create folder if not exists
    if not os.path.exists(brain_folder):
        os.mkdir(brain_folder)

    input_dest = os.path.join(brain_folder, "nnUNet_input")
    # create destination folder if not exists
    if not os.path.exists(input_dest):
        os.mkdir(input_dest)

    move_mr_scans(patient_folder, input_dest)

    # now predict
    log.info(f"Running brain mask prediction for patient {patient_id}")

    #create output folder if not exists¨
    output_dest = os.path.join(brain_folder, "output_brains")
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)
    
    # now run prediction
    nnUNet_predict(mr_task_id, input_dest, output_dest)
    

def run_ct_prediction(patient_folder : str):
    patient_id = os.path.basename(patient_folder)
    # start by moving scans
    log.info(f"Copying CT scans for patient {patient_id}")
    brain_folder = os.path.join(patient_folder, local_path_brain_ct)
    # create folder if not exists
    if not os.path.exists(brain_folder):
        os.mkdir(brain_folder)

    input_dest = os.path.join(brain_folder, "nnUNet_input")
    # create destination folder if not exists
    if not os.path.exists(input_dest):
        os.mkdir(input_dest)

    move_ct_scans(patient_folder, input_dest)

    # now predict
    log.info(f"Running brain mask prediction for patient {patient_id}")

    #create output folder if not exists¨
    output_dest = os.path.join(brain_folder, "output_brains")
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)
    
    # now run prediction
    nnUNet_predict(ct_task_id, input_dest, output_dest)

    
import os
import common.utils as utils
from common.prediction import run_prediction
import shutil
import re
import logging

log = logging.getLogger(__name__)

basepath = utils.get_path("path_data")

local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")
local_path_output_gtvs = utils.get_path("local_path_gtv")


def run_gtv_prediction(patient_folder : str, nnUNet_gtv_task_id : int):
    '''
    Run GTV prediction for all MR scans
    '''
    patient_id = os.path.basename(patient_folder)

    brainmasks_folder = os.path.join(patient_folder, local_path_brainmasks_mr)
    input_dest = os.path.join(brainmasks_folder, "nnUNet_input")
    # create nnUNet input folder if not exists
    if not os.path.exists(input_dest):
        os.mkdir(input_dest)
    #create output folder if not exists¨
    output_dest = os.path.join(patient_folder, local_path_output_gtvs)
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)
    
    # now run prediction
    log.info(f"Running GTV prediction for patient {patient_id}")
    run_prediction(brainmasks_folder, "_MR_res_stripped.nii.gz", input_dest,
                   "_gtv_0000.nii.gz", nnUNet_gtv_task_id, output_dest)
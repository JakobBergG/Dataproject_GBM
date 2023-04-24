import os
import common.utils as utils
from common.run_prediction import nnUNet_predict
import shutil
import re
import logging

log = logging.getLogger(__name__)


# task id used by nnUNet -- these are default values and can be changed
# when running setup_prediction
gtv_task_id = 600

basepath = utils.get_path("path_data")

local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")
local_path_output_gtvs = utils.get_path("local_path_output_gtvs")

def setup_prediction(nnUNet_gtv_task_id : int):
    '''
    Setup stuff required for nnUNet to run properly
    '''
    global gtv_task_id
    gtv_task_id = nnUNet_gtv_task_id
    # setup GPU 
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def move_mr_scans(masks_folder : str, destination_folder : str):
    # find MR_res scans
    patient_filelist = [f.path for f in os.scandir(masks_folder)]
    mr_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith("_MR_res_stripped.nii.gz"):
            mr_list.append(file)

    # now copy files, also changing name to comply with nnunet input requirements
    for source in mr_list:
        oldname = os.path.basename(source)
        newname = re.sub("_MR_res_stripped", "_gtv_0000", oldname)
        dest = os.path.join(destination_folder, newname)
        shutil.copy2(source, dest)


def run_prediction(patient_folder):
    '''
    Run GTV prediction for all MR scans
    '''
    patient_id = os.path.basename(patient_folder)
    # start by moving scans
    log.info(f"Copying MR scans for patient {patient_id}")
    brainmasks_folder = os.path.join(patient_folder, local_path_brainmasks_mr)
    input_dest = os.path.join(brainmasks_folder, "nnUNet_input")
    # create destination folder if not exists
    if not os.path.exists(input_dest):
        os.mkdir(input_dest)

    move_mr_scans(brainmasks_folder, input_dest)

    #create output folder if not exists¨
    output_dest = os.path.join(patient_folder, local_path_output_gtvs)
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)
    
    # now predict
    log.info(f"Running gtv prediction for patient {patient_id}")

    # now run prediction
    nnUNet_predict(gtv_task_id, input_dest, output_dest)

    
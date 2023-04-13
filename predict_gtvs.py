import os
import utils
import shutil
import re

GTV_TASK_ID = 600

# setup GPU 
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

basepath = utils.get_path("path_data")

local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")
local_path_output_gtvs = utils.get_path("local_path_output_gtvs")

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
        newname = re.sub("_MR_res_stripped", "_MR_res_stripped_0000", oldname)
        dest = os.path.join(destination_folder, newname)
        shutil.copy2(source, dest)


def predict_gtv(task_id : int, input_folder : str, output_folder : str):
    # nnUNet_predict runs for all scans in subfolder
    command = f"nnUNet_predict -i {input_folder} -o {output_folder} -t {task_id} -f 0 -tr nnUNetTrainerV2 -m 3d_fullres"
    os.system(command)


patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]

for patient in patientfolders:
    patient_id = os.path.basename(patient)
    # start by moving scans
    print(f"Copying MR scans for patient {patient_id}")
    brainmasks_folder = os.path.join(patient, local_path_brainmasks_mr)
    input_dest = os.path.join(brainmasks_folder, "nnUNet_input")
    # create destination folder if not exists
    if not os.path.exists(input_dest):
        os.mkdir(input_dest)

    move_mr_scans(brainmasks_folder, input_dest)

    # now predict
    print(f"Running gtv prediction for patient {patient_id}")

    #create output folder if not exists¨
    output_dest = os.path.join(patient, local_path_output_gtvs)
    if not os.path.exists(output_dest):
        os.mkdir(output_dest)
    
    # now run prediction
    predict_gtv(GTV_TASK_ID, input_dest, output_dest)

    
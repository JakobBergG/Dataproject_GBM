import os
import utils
import argparse
import shutil
import re

parser = argparse.ArgumentParser()
parser.add_argument("--ct",
                    help="predict brain masks for ct scans",
                    action="store_true")
parser.add_argument("--mr",
                    help="predict brain masks for mr scans",
                    action="store_true")
args = parser.parse_args()

if not (args.ct or args.mr):
    print("You must either specify either --ct or --mr or both as command line argument")
    print("The brain masks will be predicted for the specified scan type(s).")
    quit()

CT_TASK_ID = 800
MR_TASK_ID = 801

# setup GPU 
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

basepath = utils.get_path("path_data")

local_path_brain_ct = utils.get_path("local_path_brain_ct")
local_path_brain_mr = utils.get_path("local_path_brain_mr")


def move_mr_scans(patient_folder : str, destination_folder : str):
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
    # find CT_res scans
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


def predict_brain_mask(task_id : int, input_folder : str, output_folder : str):
    # nnUNet_predict runs for all scans in subfolder
    command = f"nnUNet_predict -i {input_folder} -o {output_folder} -t {task_id} -f 0 -tr nnUNetTrainerV2 -m 3d_fullres"
    os.system(command)


patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]

if args.mr:
    for patient in patientfolders:
        patient_id = os.path.basename(patient)
        # start by moving scans
        print(f"Copying MR scans for patient {patient_id}")
        brain_folder = os.path.join(patient, local_path_brain_mr)
        # create folder if not exists
        if not os.path.exists(brain_folder):
            os.mkdir(brain_folder)

        input_dest = os.path.join(brain_folder, "nnUNet_input")
        # create destination folder if not exists
        if not os.path.exists(input_dest):
            os.mkdir(input_dest)

        move_mr_scans(patient, input_dest)

        # now predict
        print(f"Running brain mask prediction for patient {patient_id}")

        #create output folder if not exists¨
        output_dest = os.path.join(brain_folder, "output_brains")
        if not os.path.exists(output_dest):
            os.mkdir(output_dest)
        
        # now run prediction
        predict_brain_mask(MR_TASK_ID, input_dest, output_dest)
    

if args.ct:
    for patient in patientfolders:
        patient_id = os.path.basename(patient)
        # start by moving scans
        print(f"Copying CT scans for patient {patient_id}")
        brain_folder = os.path.join(patient, local_path_brain_ct)
        # create folder if not exists
        if not os.path.exists(brain_folder):
            os.mkdir(brain_folder)

        input_dest = os.path.join(brain_folder, "nnUNet_input")
        # create destination folder if not exists
        if not os.path.exists(input_dest):
            os.mkdir(input_dest)

        move_ct_scans(patient, input_dest)

        # now predict
        print(f"Running brain mask prediction for patient {patient_id}")

        #create output folder if not exists¨
        output_dest = os.path.join(brain_folder, "output_brains")
        if not os.path.exists(output_dest):
            os.mkdir(output_dest)
        
        # now run prediction
        predict_brain_mask(CT_TASK_ID, input_dest, output_dest)

    
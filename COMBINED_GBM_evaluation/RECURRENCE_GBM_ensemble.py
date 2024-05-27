# I will now ensemble combinations of the following models:
#  ['3d_fullres']
# 3d_fullres 0.7278832537880017
# Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM submit model 3d_fullres 0.7278832537880017

# Here is how you should predict test cases. Run in sequential order and replace all input and output folder names with your personalized ones

# nnUNet_predict -i FOLDER_WITH_TEST_CASES -o OUTPUT_FOLDER_MODEL1 -tr nnUNetTrainerV2 -ctr nnUNetTrainerV2CascadeFullRes -m 3d_fullres -p nnUNetPlansv2.1 -t Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM

import os
import nnunet
import subprocess

dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)

TEST_FOLDER_WITH_TEST_CASES = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/imagesTs"
OUTPUT_FOLDER_MODEL1 = "C:/Users/Student1/Desktop/ensemble_test"
command = ["nnUNet_predict", "-i", TEST_FOLDER_WITH_TEST_CASES, "-o", OUTPUT_FOLDER_MODEL1,
           "-tr", "nnUNetTrainerV2", "-ctr", "nnUNetTrainerV2CascadeFullRes", "-m", "3d_fullres",
           "-p", "nnUNetPlansv2.1", "-t", "Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM"]

subprocess.run(command)

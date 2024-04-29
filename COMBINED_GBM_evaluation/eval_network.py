import logging
import subprocess
import os
import re


#######
# Select which network to evaluate throgh these variables

task_id = 806
task_name = "Task806_ANOUK_GBM"
input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task805_COMBINED_GBM/imagesTs"
gt_folder = ""
output_folder = os.path.join("D:/GBM/COMBINED_GBM_predictions", task_name)


#######
# evaluate network

command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
                "3d_fullres"]
subprocess.run(command)
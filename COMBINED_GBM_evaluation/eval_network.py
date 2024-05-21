import logging
import subprocess
import os
import re


#######
# Select which network to evaluate throgh these variables

task_id = 812
#task_name = "Task810_RECURRENCE_DIALATED_GBM"
input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/imagesTs"
gt_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/labelsTs"
#output_folder = os.path.join("D:/GBM/RECURRENCE_DIALATED_GBM_predictions", task_name)
output_folder = "D:/GBM/COMBINED_GBM_predictions/Task812_RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM_fold_1"

#######
# evaluate network

command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
                "3d_fullres", "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
subprocess.run(command)
import logging
import subprocess
import os
import re
import nnunet.evaluation.evaluator

#######
# Select which network to evaluate throgh these variables

task_id = 806
#task_name = "Task810_RECURRENCE_DIALATED_GBM"
input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/imagesTs"
gt_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/labelsTs"
#output_folder = os.path.join("D:/GBM/RECURRENCE_DIALATED_GBM_predictions", task_name)

output_folder = f"D:/GBM/GBM_predictions/Task806_ANOUK_GBM_on_RECURRENCE"

#######
# make predictions

command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
                "3d_fullres", "-z"]# , "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
subprocess.run(command)


# compute the metrics (will be saved as a summary.json file)
REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/labelsTs"
PRED = "D:/GBM/GBM_predictions/Task806_ANOUK_GBM_on_RECURRENCE"
L = (1,)

# The evaluator class has been modified so all metrics are calculated. (also msd, hd, hd95)
# Use the nnUNet_evaluate_folder command to evaluate models.

command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]

subprocess.run(command)
import os
import nnunet
import subprocess


dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)

# # Finetune CUH_GBM with learning rate of 1e-6, 350 epochs
# command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2_copy_2", "Task811_CUH_GBM", "1", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
# subprocess.run(command)

# # finetune fold 3 and 4 in RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM for another 100 epochs. (250 epochs in total)
# for fold in ["3","4"]:
#     command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2", "Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM", fold, "--npz", "--continue_training" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
#     subprocess.run(command)


# # WE WILL NOT FINETUNE AUH_GBM BECAUSE THE ANOUK TRAINING SET AND AUH TEST SET ARE OVERLAPPING
# # Finetune AUH_GBM with learning rate of 1e-6, 350 epochs
# # command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2_copy_2", "Task809_OUH_GBM", "1", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
# # subprocess.run(command)

# # Generate ensemble predictions from the RECURRENCE_GBM:

# TEST_FOLDER_WITH_TEST_CASES = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/imagesTs"
# OUTPUT_FOLDER_MODEL1 = "D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble"
# command = ["nnUNet_predict", "-i", TEST_FOLDER_WITH_TEST_CASES, "-o", OUTPUT_FOLDER_MODEL1,
#            "-tr", "nnUNetTrainerV2", "-ctr", "nnUNetTrainerV2CascadeFullRes", "-m", "3d_fullres",
#            "-p", "nnUNetPlansv2.1", "-t", "Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM"]

# subprocess.run(command)



# MANGLER
# Generate predictions from the OUH_GBM
input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task809_OUH_GBM/imagesTs"
output_folder = "D:/GBM/GBM_predictions/Task809_OUH_GBM"
task_id = 809
command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "1", "-tr", "nnUNetTrainerV2_copy_2", "-m",
                "3d_fullres"] #, "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
subprocess.run(command)


# MANGLER
# Generate predictions from the CUH_GBM
input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task811_CUH_GBM/imagesTs"
output_folder = "D:/GBM/GBM_predictions/Task811_CUH_GBM"
task_id = 811
command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "1", "-tr", "nnUNetTrainerV2_copy_2", "-m",
                "3d_fullres"] #, "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
subprocess.run(command)

# # WE WILL NOT GENERATE PREDICTIONS FOR AUH_GBM BECAUSE THE ANOUK TRAINING SET AND AUH TEST SET ARE OVERLAPPING
# # Generate predictions from the AUH_GBM
# # input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task811_CUH_GBM/imagesTs"
# # output_folder = "D:/GBM/GBM_predictions/Task811_CUH_GBM"
# # task_id = 811
# # command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
# #                 str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
# #                 "3d_fullres"] #, "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
# # subprocess.run(command)

# # Generate predictions from the ANOUK_GBM on the whole test set from COMBINED_GBM (except recurrence images).
# input_folder = "E:/Jasper/nnUNet/nnUNet_raw_data/Task805_COMBINED_GBM/imagesTs_no_recurrence"
# output_folder = "D:/GBM/GBM_predictions/Task806_ANOUK_GBM"
# task_id = 806
# command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
#                 str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
#                 "3d_fullres"] #, "-chk", "model_best"] # The last part is for the unfinished folds (RECURRENCE_DIALATED_GBM for example)
# subprocess.run(command)

# # Compute metrics for Task812_GBM predictions
# REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/labelsTs"
# PRED = "D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble"

# command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]
# subprocess.run(command)

# MANGLER
# Compute metrics for ANOUK_GBM predictions
REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task805_COMBINED_GBM/labelsTs_no_recurrence"
PRED = "D:/GBM/GBM_predictions/Task806_ANOUK_GBM"

command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]
subprocess.run(command)

# MANGLER
# Compute metrics for CUH_GBM predictions
REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task811_CUH_GBM/labelsTs"
PRED = "D:/GBM/GBM_predictions/Task811_CUH_GBM"

command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]
subprocess.run(command)

# MANGLER
# Compute metrics for OUH_GBM predictions
REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task809_OUH_GBM/labelsTs"
PRED = "D:/GBM/GBM_predictions/Task809_OUH_GBM"

command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]
subprocess.run(command)

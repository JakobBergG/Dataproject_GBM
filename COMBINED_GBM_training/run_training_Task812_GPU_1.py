import os
import nnunet
import subprocess


dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)
#nnUNet_train 3d_fullres nnUNetTrainerV2 TaskXXX_MYTASK FOLD --npz

# Finetune the recurrence network
# for fold in ["3","4"]:
#     command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2", "Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM", fold, "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
#     subprocess.run(command)

# Finetune CUH_GBM with learning rate of 1e-5, 350 epochs
# command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2_copy", "Task811_CUH_GBM", "0", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
# subprocess.run(command)


# finetune fold 3 and 4 in RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM for another 100 epochs. (250 epochs in total)
for fold in ["3","4"]:
    command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2", "Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM", fold, "--npz", "--continue_training" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
    subprocess.run(command)



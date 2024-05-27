import os
import nnunet
import subprocess


dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

os.chdir(main_dir)

#nnUNet_train 3d_fullres nnUNetTrainerV2 TaskXXX_MYTASK FOLD --npz
# PROBLEMS:
# CHANGE LEARNING RATE TO SMALLER
#command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2", "Task809_OUH_GBM", "3", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
#subprocess.run(command)


# Finetune OUH_GBM with learning rate of 1e-5, 350 epochs
# command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2_copy", "Task809_OUH_GBM", "0", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
# subprocess.run(command)

# Finetune OUH_GBM with learning rate of 1e-6, 350 epochs
command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2_copy_2", "Task809_OUH_GBM", "1", "--npz" ,"-pretrained_weights", "E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task806_ANOUK_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_0/model_best.model"]
subprocess.run(command)





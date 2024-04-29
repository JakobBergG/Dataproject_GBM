import os
import nnunet
import subprocess


dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)
#nnUNet_train 3d_fullres nnUNetTrainerV2 TaskXXX_MYTASK FOLD --npz
command = ["nnUNet_train", "3d_fullres", "nnUNetTrainerV2", "Task806_ANOUK_GBM", "0", "--npz", "-c"]


subprocess.run(command)
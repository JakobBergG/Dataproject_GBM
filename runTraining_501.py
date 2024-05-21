# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 10:12:44 2022

@author: jasper
"""

import os
import nnunet
dirname = 'c:\\'
main_dir = os.path.join(dirname, 'users', 'Jasper','anaconda3','Lib','site-packages','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)

#%%
!nnUNet_plan_and_preprocess -t 510 --verify_dataset_integrity

#%%

!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task502_BREASTDECT\fold_0 -t 502 -f 0 -tr nnUNetTrainerV2 -m 2d --save_npz

#%%

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 510 0 --npz

#%%
!nnUNet_train 2d nnUNetTrainerV2_Jasper 510 0 --npz
#%%

!nnUNet_train 2d nnUNetTrainerV2 510 0 --npz



# !nnUNet_train 2d nnUNetTrainerCE 504 0 --npz

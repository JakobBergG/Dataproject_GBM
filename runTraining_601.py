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
!nnUNet_plan_and_preprocess -t 601 --verify_dataset_integrity

!nnUNet_plan_and_preprocess -t 602 --verify_dataset_integrity

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 601 0 --npz

nnUNet_train 2d nnUNetTrainerV2_Jasper 601 0 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 602 0 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 600 1 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 601 1 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 602 1 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 600 2 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 601 2 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 602 2 --npz

#%%

!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task600_ProbAD\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task600_ProbAD\fold_0 -t 600 -f 0 -tr nnUNetTrainerV2_noDataAugmentation -m 2d --save_npz
#%%
!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task600_ProbAD\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task600_ProbAD\fold_1 -t 600 -f 1 -tr nnUNetTrainerV2_noDataAugmentation -m 2d --save_npz
#%%
!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task601_ProbGL\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task601_ProbGL\fold_0 -t 601 -f 0 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task601_ProbGL\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task601_ProbGL\fold_1 -t 601 -f 1 -tr nnUNetTrainerV2_noDataAugmentation -m 2d --save_npz

!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task602_ProbCA\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task602_ProbCA\fold_0 -t 602 -f 0 -tr nnUNetTrainerV2_noDataAugmentation -m 2d --save_npz
!nnUNet_predict -i E:\Jasper\nnUNet\nnUNet_raw_data\Task602_ProbCA\ImagesTs -o E:\Jasper\nnUNet\nnUNet_prediction_results\Task602_ProbCA\fold_1 -t 602 -f 1 -tr nnUNetTrainerV2_noDataAugmentation -m 2d --save_npz

#%%
!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 600 3 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 601 3 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 600 4 --npz

!nnUNet_train 2d nnUNetTrainerV2_noDataAugmentation 601 4 --npz


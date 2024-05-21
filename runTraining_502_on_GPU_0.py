# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 10:12:44 2022

@author: jasper
"""

import os
import nnunet
dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)

#%%
!nnUNet_plan_and_preprocess -t 502 --verify_dataset_integrity
#%%
# for FOLD in [1, 2, 3, 4], run():
!nnUNet_train 2d nnUNetTrainerV2 502 2 --npz
!nnUNet_train 2d nnUNetTrainerV2 502 3 --npz
#%%

!nnUNet_find_best_configuration -m 2d -t 502 --strict

#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_0 -t 502 -f 0 -tr nnUNetTrainerV2 -m 2d --save_npz

!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_1 -t 502 -f 1 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_2 -t 502 -f 2 -tr nnUNetTrainerV2 -m 2d --save_npz

!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_3 -t 502 -f 3 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task502_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_4 -t 502 -f 4 -tr nnUNetTrainerV2 -m 2d --save_npz


#%%


main_dir = os.path.join(dirname, 'Jasper','nnUnet','nnUNet_prediction_results','Task502_BREASTDECT')
os.chdir(main_dir)
# !nnUNet_ensemble -f "e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_0" "e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_1" "e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_2" -o "e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\ensemble"☺

!nnUNet_ensemble -f e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_0 e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_1 e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_2 e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_3 e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\fold_4 -o e:\jasper\nnUnet\nnUNet_prediction_results\Task502_BREASTDECT\ensemble
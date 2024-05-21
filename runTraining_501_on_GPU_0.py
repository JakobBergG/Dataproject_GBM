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
# for FOLD in [1, 2, 3, 4], run():
#%%
!nnUNet_train 2d nnUNetTrainerV2 501 0 -c --npz
!nnUNet_train 2d nnUNetTrainerV2 501 4 --npz
#%%

!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task501_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_0 -t 501 -f 0 -tr nnUNetTrainerV2 -m 2d --save_npz
# !nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task501_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_1 -t 501 -f 1 -tr nnUNetTrainerV2 -m 2d --save_npz
# !nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task501_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_2 -t 501 -f 2 -tr nnUNetTrainerV2 -m 2d --save_npz
# !nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task501_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_3 -t 501 -f 3 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\Task501_BREASTDECT\ImagesTs -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_4 -t 501 -f 4 -tr nnUNetTrainerV2 -m 2d --save_npz

#%%
!nnUNet_ensemble -f e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_0 e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_1 e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_2 e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_3 e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\fold_4 -o e:\jasper\nnUnet\nnUNet_prediction_results\Task501_BREASTDECT\ensemble
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
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_1 -t 501 -f 1 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_2 -t 501 -f 2 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_3 -t 501 -f 3 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_ensemble -f e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_1 e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_2 e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\fold_3 -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\501\ensemble
#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet_cosine -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_0 -t 502 -f 0 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet_cosine -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_1 -t 502 -f 1 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet_cosine -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_2 -t 502 -f 2 -tr nnUNetTrainerV2 -m 2d --save_npz
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet_cosine -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_3 -t 502 -f 3 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_predict -i e:\jasper\nnUnet\nnUNet_raw_data\validation_data\nnUNet_cosine -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_4 -t 502 -f 4 -tr nnUNetTrainerV2 -m 2d --save_npz
#%%
!nnUNet_ensemble -f e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_0 e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_1 e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_2 e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_3 e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\fold_4 -o e:\jasper\nnUnet\nnUNet_prediction_results\validation\502\ensemble

import os
import common.utils as utils
import SimpleITK as sitk
import re

# TODO: remove holes here
# TODO: Get mask files directly

basepath = utils.get_path("path_data")

local_path_brainmasks_ct = utils.get_path("local_path_brainmasks_ct")
local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")

def remove_small_object_and_save(mask_path: str, output_path: str):
    '''removes small object from mask image and saves new mask'''
    mask=sitk.ReadImage(mask_path)
    connected_component = sitk.ConnectedComponentImageFilter()
    component_image = connected_component.Execute(mask)

    label_component = sitk.RelabelComponentImageFilter()
    label_image = label_component.Execute(component_image) == 1
    sitk.WriteImage(label_image, output_path)
    

def cleanup_brain_mask(patient_folder : str):
     '''
     Cleans up all brain masks for patient data path patient_folder
     '''
    
     path_mr = os.path.join(patient_folder,local_path_brainmasks_mr)  
     path_ct = os.path.join(patient_folder,local_path_brainmasks_ct)  
     

     # find all files in mask folder
     mr_filelist = [f.path for f in os.scandir(path_mr)]
     ct_filelist = [f.path for f in os.scandir(path_ct)]
    
     # find masks
     mr_list = []
     ct = ''
     
     for file in mr_filelist:
         if os.path.basename(file).endswith("_MR_res_mask.nii.gz"):
             mr_list.append(file)
        
     for file in ct_filelist:
        if os.path.basename(file).endswith("_CT_res_mask.nii.gz"):
            ct = file
 
     # clean and save masks
     for mr in mr_list:
        output_name = re.sub("_MR_res_mask", "_MR_res_mask_cleaned", mr)
        remove_small_object_and_save(mr, output_name)
        
        


     output_name = re.sub("_CT_res_mask", "_CT_res_mask_cleaned", ct)
     remove_small_object_and_save(ct, output_name)
    
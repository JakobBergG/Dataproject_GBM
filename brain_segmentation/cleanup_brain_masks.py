import os
import common.utils as utils
import SimpleITK as sitk
import re
import logging

log = logging.getLogger(__name__)

basepath = utils.get_path("path_data")

local_path_brainmasks_ct = utils.get_path("local_path_brainmasks_ct")
local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")

def remove_small_object_and_save(mask_path: str, output_path: str, patient_id):
    '''removes small object from mask image and saves new mask'''
    mask=sitk.ReadImage(mask_path)
    # The connected component filters labels each connected bit of the mask
    # 1, 2, 3, etc. respecitively
    connected_component = sitk.ConnectedComponentImageFilter()
    component_image = connected_component.Execute(mask)
    # Relabel the components so that 1 is the largest, 2 is the next-largest etc
    label_component = sitk.RelabelComponentImageFilter()
    n_components = connected_component.GetObjectCount()
    if n_components > 1: # if there is more than 1 component, we have separate "blobs"
        log.warning(f"Patient {patient_id} has {n_components - 1} small object(s) in brain mask. Removing...")
        
    # Only take the largest component
    label_image = label_component.Execute(component_image) == 1
    sitk.WriteImage(label_image, output_path)


    

def cleanup_brain_mask(patient_folder : str):
     '''
     Cleans up all brain masks for patient data path patient_folder
     '''
     patient_id = os.path.basename(patient_folder)
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
     # mr masks
     for mr in mr_list:
        output_name = re.sub("_MR_res_mask", "_MR_res_mask_cleaned", mr)
        remove_small_object_and_save(mr, output_name, patient_id)
        
     # ct mask
     output_name = re.sub("_CT_res_mask", "_CT_res_mask_cleaned", ct)
     remove_small_object_and_save(ct, output_name, patient_id)
    
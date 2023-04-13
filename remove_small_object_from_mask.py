import os
import utils
import SimpleITK as sitk
import re



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
    





# Run for the type of scans we want
patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]
for patient in patientfolders:
     
     patient_id = os.path.basename(patient)
     
     if patient_id != "0114":
         break
     
     # find all masks
     patient_filelist = [f.path for f in os.scandir(patient)]
     mr_list = []
     for file in patient_filelist:
         if os.path.basename(file).endswith("_MR_res.nii.gz"):
             mr_list.append(file)
     ct_list = []
     for file in patient_filelist:
        if os.path.basename(file).endswith("_CT_res.nii.gz"):
            ct_list.append(file)
     
        
     
     for mr in mr_list:
        mr_name = os.path.basename(mr)
        mask_name = re.sub("_MR_res", "_MR_res_mask", mr_name)
        output_name = re.sub("_MR_res_mask", "_MR_res_mask_cleaned", mask_name)
        mask_path = os.path.join(patient, local_path_brainmasks_mr, mask_name)
        output_path = os.path.join(patient, local_path_brainmasks_mr, output_name)
        remove_small_object_and_save(mask_path, output_path)
        
     for ct in ct_list:
        ct_name = os.path.basename(ct)
        mask_name = re.sub("_CT_res", "_CT_res_mask", mr_name)
        output_name = re.sub("_CT_res_mask", "_CT_res_mask_cleaned", mask_name)
        mask_path = os.path.join(patient, local_path_brainmasks_ct, mask_name)
        output_path = os.path.join(patient, local_path_brainmasks_ct, output_name)
        remove_small_object_and_save(mask_path, output_path)
        
    
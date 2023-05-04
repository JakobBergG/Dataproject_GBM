import os
import common.utils as utils
import SimpleITK as sitk
import argparse
import re
import logging

log = logging.getLogger(__name__)

basepath = utils.get_path("path_data")

local_path_brainmasks_ct = utils.get_path("local_path_brainmasks_ct")
local_path_brainmasks_mr = utils.get_path("local_path_brainmasks_mr")

def strip_skull_and_save(scan_path : str , mask_path : str, dilation_radius : tuple, output_path : str):
    '''Dilate mask image a little bit and save the file'''
    scan = sitk.ReadImage(scan_path)
    mask = sitk.ReadImage(mask_path)

    # dilate brain mask so we get a little bit more of the brain in the stripped skull
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelType(sitk.sitkBall)
    dilate_filter.SetKernelRadius(dilation_radius)
    dilate_filter.SetForegroundValue(1) 
    bigger_mask = dilate_filter.Execute(mask)
    stripped_skull = sitk.Mask(scan, bigger_mask) 
    sitk.WriteImage(stripped_skull, output_path)

def run_skull_stripping(patient_folder):
    '''
    Skullstrip all MR scans for patient
    '''
    patient_id = os.path.basename(patient_folder)
    log.info(f"Stripping MR skulls for patient {patient_id}")
    # find all mr scans
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    mr_list = []
    ct_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith("_MR_res.nii.gz"):
            mr_list.append(file)
        if os.path.basename(file).endswith("_CT_res.nii.gz"):
            ct_list.append(file)

    # now strip mr skulls
    mr_dilation_radius = utils.get_setting("skull_stripping_dilation_radius_mr")
    for mr in mr_list:
        mr_name = os.path.basename(mr)
        mask_name = re.sub("_MR_res", "_MR_res_mask_cleaned", mr_name)
        output_name = re.sub("_MR_res", "_MR_res_stripped", mr_name)
        mask_path = os.path.join(patient_folder, local_path_brainmasks_mr, mask_name)
        output_path = os.path.join(patient_folder, local_path_brainmasks_mr, output_name)
        strip_skull_and_save(mr, mask_path, mr_dilation_radius, output_path)
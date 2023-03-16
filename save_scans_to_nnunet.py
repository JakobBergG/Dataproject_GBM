#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import SimpleITK as sitk
import utils


scans = ["0114","0540"]


data_path=os.path.join("../nii_preprocessed")

outpath=os.path.join("E:","Jasper","nnUNet","nnUNet_raw_data")

outpath_CT=os.path.join(outpath,"Task800_GBM")
outpath_MR=os.path.join(outpath,"Task801_GBM")



dilate_filter = sitk.BinaryDilateImageFilter()
dilate_filter.SetKernelType(sitk.sitkBall)
dilate_filter.SetKernelRadius((2,2,2))
dilate_filter.SetForegroundValue(1)

erode_filter=sitk.BinaryErodeImageFilter()
erode_filter.SetKernelType(sitk.sitkBall)
erode_filter.SetKernelRadius((2,2,2))
erode_filter.SetForegroundValue(1)


i=1
MR_list=[]
for s in scans:
    MR_list=[]
    patient_folder=os.path.join(data_path,s)
    
    patient_filelist =[ f.path for f in os.scandir(patient_folder)]
    for file in patient_filelist:
        if file.endswith("_CT_res.nii.gz"):
            CT=sitk.ReadImage(file)
        elif file.endswith("_CT_brain.nii.gz"):
            CT_brain=sitk.ReadImage(file)
        elif file.endswith("_MR_res.nii.gz"):
            MR_list.append(file)
        
    
    MR=sitk.ReadImage(sorted(MR_list)[-2])
    
    CT_folder=os.path.join(patient_folder, "CT_TO_MR")
    MR_brain =sitk.ReadImage(sorted([ f.path for f in os.scandir(CT_folder) if f.path.endswith("_BRAIN_res.nii.gz")])[-2])
    
    CT_brain=utils.reslice_image(CT_brain, CT)
    
    CT_brain=dilate_filter.Execute(CT_brain)
    CT_brain=erode_filter.Execute(CT_brain)
    
    MR_brain=dilate_filter.Execute(MR_brain)
    MR_brain=erode_filter.Execute(MR_brain)
    
    
    
    
    
    number="{:04d}".format(i)
    
    CT_brain_out=os.path.join(outpath_CT,"GBM_%s.nii.gz" %number)
    CT_out=os.path.join(outpath_CT,"GBM_%s_0000.nii.gz" %number)
    
    MR_brain_out=os.path.join(outpath_MR,"GBM_%s.nii.gz" %number)
    MR_out=os.path.join(outpath_MR,"GBM_%s_0000.nii.gz" %number)
    
    sitk.WriteImage(CT_brain, CT_brain_out)
    sitk.WriteImage(CT, CT_out)

    sitk.WriteImage(MR_brain, MR_brain_out)
    sitk.WriteImage(MR, MR_out)    

    i+=1

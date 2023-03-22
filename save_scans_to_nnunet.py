#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import SimpleITK as sitk
import utils


scans_int = [4733, 3770, 540, 4786, 5166,
4409, 4081, 3462, 3856, 3424,
4225, 1400, 3249, 3728, 4361,
3862, 4191, 1702, 3743, 4404,
3445, 4120, 3459, 3322, 4385,
5075, 3334, 4537, 4040, 5094,
1838, 4630, 4234, 5071, 5061,
5497, 4542, 315, 3886, 5171,
3755, 4809, 4665, 5302, 4462,
2080, 4788, 3442, 4625, 4285,
3136, 4630, 3791, 4850, 4057,
3686, 4233, 3287, 4234, 5068,
3931, 4223, 1124, 5265, 4114,
3989, 4150, 4215, 4548, 4147, 
3525, 4018, 4147, 5274, 5399, 
4713, 3402, 4939, 3433, 4975, 
4099, 4267, 4435, 5412, 4761,
5373, 4498, 4106, 4787, 4748, 
5214, 4375, 5250, 4722, 3212, 
3657, 3719, 5038, 3823, 4340
]
scans=[]
for scan in scans_int:
    scans.append("{:04d}".format(scan))


data_path=os.path.join("../nii_preprocessed")

outpath=os.path.join("e:\\","Jasper","nnUNet","nnUNet_raw_data")

outpath_CT=os.path.join(outpath,"Task800_GBM")
outpath_MR=os.path.join(outpath,"Task801_GBM")



dilate_filter = sitk.BinaryDilateImageFilter()
dilate_filter.SetKernelType(sitk.sitkBall)
dilate_filter.SetKernelRadius((5,5,2))
dilate_filter.SetForegroundValue(1)

erode_filter=sitk.BinaryErodeImageFilter()
erode_filter.SetKernelType(sitk.sitkBall)
erode_filter.SetKernelRadius((5,5,2))
erode_filter.SetForegroundValue(1)

fillholl_filter=sitk.BinaryFillholeImageFilter()




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
    CT_brain=fillholl_filter.Execute(CT_brain)
    
   
    
    MR_brain=dilate_filter.Execute(MR_brain)
    MR_brain=erode_filter.Execute(MR_brain)
    MR_brain=fillholl_filter.Execute(MR_brain)

    
    
    
    
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

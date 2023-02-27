#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 11:16:29 2023

@author: bjarkekjaer
"""
import SimpleITK as sitk
import numpy as np
import os
import metrics
import utils
from medpy import metric


basepath = os.path.join('data')

#Selecting only one patient (0114)
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
patient=patientfolders[1]
patientid = os.path.basename(patient)





#Find dose file
filelist = [ f.path for f in os.scandir(patient) if f.is_file()]
dose_file = ''

for pathstr in filelist:
    if os.path.basename(pathstr).endswith('RTDOSE_res.nii.gz'):
        dose_file = pathstr

    
#Find GTV at T3
CT_path = os.path.join(patient, "MR_TO_CT")
CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
gtvlist = []

for pathstr in CT_filelist:
    if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
         gtvlist.append(pathstr)

#Assumes the last file in list is the last GTV
rec = sitk.ReadImage(gtvlist[-1])



#Read dose and convert to 0.95-mask 
dose_image = sitk.ReadImage(dose_file)
target metrics.get_target_dose(dose_image) 
dose_95 = metrics.dose_percentage_region(dose_image, target, 0.95)

#Resample GTV to match dose mask dimensions (MIGHT NEED MORE ARGUMENTS)
rec = utils.reslice_image(rec, dose_95, is_label = True)


#Overlap 

print(f"Percentage of gtv in 95% dose area: {metrics.mask_overlap(rec, dose_95)}")


dose = sitk.GetArrayViewFromImage(dose_95)
rec = sitk.GetArrayViewFromImage(rec)


print(f"Jaccard coefficent: {metric.jc(rec,dose)}")



#Saving dose mask in patient folder
#outfile = dose_file.replace('RTDOSE_', 'DOSEMASK_')


#sitk.WriteImage(dose, outfile)



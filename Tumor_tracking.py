#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:33:57 2023

@author: bjarkekjaer
"""


import SimpleITK as sitk
import numpy as np
import os
from medpy import metric
import metrics
import utils





basepath = os.path.join('data')

#Selecting only one patient (1400)
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
patient=patientfolders[3]
patientid = os.path.basename(patient)



    
#Find GTVs
CT_path = os.path.join(patient, "MR_TO_CT")
CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
gtvlist = []

for pathstr in CT_filelist:
    if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
         gtvlist.append(pathstr)
         
baseline = sitk.ReadImage(gtvlist[-2])
rec = sitk.ReadImage(gtvlist[-1])



total_volume_baseline = metrics.volume_mask_cc(baseline)


baseline_component = sitk.ConnectedComponent()
baseline_component = sitk.RelabelComponent(baseline_component,10)


volume_pr_lession_baseline = metrics.volume_component_cc(baseline)









              





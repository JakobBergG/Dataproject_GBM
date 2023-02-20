#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 08:49:23 2023

@author: bjarkekjaer
"""

import SimpleITK as sitk
import numpy as np
import os






basepath = os.path.join('data')

#Selecting only one patient (0114)
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
patient=patientfolders[1]
patientid = os.path.basename(patient)



    
#Find GTVs
CT_path = os.path.join(patient, "MR_TO_CT")
CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
gtvlist = []

for pathstr in CT_filelist:
    if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
         gtvlist.append(pathstr)

#Assumes the last file in list is the last GTV

T2_gtv = sitk.ReadImage(gtvlist[-2])
T3_gtv = sitk.ReadImage(gtvlist[-1])


hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()


hausdorff_distance_filter.Execute(T2_gtv, T3_gtv)




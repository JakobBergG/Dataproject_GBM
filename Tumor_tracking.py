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
         
gtv1 = sitk.ReadImage(gtvlist[0])
gtv2 = sitk.ReadImage(gtvlist[1])




component_image = sitk.ConnectedComponent(gtv1)



#component_image = sitk.RelabelComponent(component_image,1, sortByObjectSize=True)




stats = sitk.LabelShapeStatisticsImageFilter()
stats.Execute(component_image)


label_sizes = [stats.GetNumberOfPixels(l) for l in stats.GetLabels() ]
              




outfile = os.path.join(patient,"COMPONENT_GTV.nii.gz")

sitk.WriteImage(component_image, outfile)


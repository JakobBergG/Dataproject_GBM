
import os
import SimpleITK as sitk
import numpy as np
import json
import common.utils as utils


SAVE_AS_JSON = True

# Loading all patient folders
basepath = utils.get_path("path_data")
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]


# List of used metrics
metriclist = ['Mattes50', 'Mattes40', 'Mattes30', 'Mattes20', 'Hist50', 'Hist40', 'Hist30',
           'Hist20', 'Zero'] 

# Define function to calculate metric
def calcMI(fixed, moving, metric='Mattes50'):
    score = 0.0
    if metric == 'Mattes50':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins = 50)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Mattes40':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins = 40)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Mattes30':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins = 30)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Mattes20':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins = 20)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    
    if metric == 'Hist50':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsJointHistogramMutualInformation(numberOfHistogramBins = 50)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Hist40':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsJointHistogramMutualInformation(numberOfHistogramBins = 40)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Hist30':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsJointHistogramMutualInformation(numberOfHistogramBins = 30)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    if metric == 'Hist20':
        try:
            registration_method = sitk.ImageRegistrationMethod()
            registration_method.SetMetricAsJointHistogramMutualInformation(numberOfHistogramBins = 20)
            score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
        except:
            print('failed')
    

    return score

# Creating dictionary with each patient_id as index 
patient_dic = {}

for patient in patientfolders:
    patient_id = os.path.basename(patient)
    patient_dic[patient_id] = {}
    
    # Path to file with cropped MR to CT images
    cropfilepath = os.path.join(patient, 'CroppedImages_MR_to_CT')
    
    # Loop over all the files in the patient folder
    filelist = [ f.path for f in os.scandir(cropfilepath) if f.is_file() ]
    
    # Save all MR and CT files to different list
    ctlist = []
    mrlist1 = []
    mrlist2 = []
    for pathstr in filelist:
        if os.path.basename(pathstr).startswith('CT'):
            ctlist.append(pathstr)
        if os.path.basename(pathstr).startswith('MR1'):
            mrlist1.append(pathstr)
        if os.path.basename(pathstr).startswith('MR2'):
            mrlist2.append(pathstr)
            
    
    # Loop over all mr and calculate each metric
    for i in range(len(mrlist1)):
        mr1 = sitk.ReadImage(mrlist1[i])
        mr2 = sitk.ReadImage(mrlist2[i])
        ct1 = sitk.ReadImage(ctlist[0])
        ct2 = sitk.ReadImage(ctlist[0])
        for metric in metriclist:
            if metric == 'Zero':
                im_view = sitk.GetArrayViewFromImage(mr2)
                part_zero = 1 - (np.count_nonzero(im_view) / im_view.size)
                patient_dic[patient_id][metric] = patient_dic[patient_id].get(metric, []) \
                    + [part_zero]
            else:
                patient_dic[patient_id][metric] = patient_dic[patient_id].get(metric, []) \
                    + [min(calcMI(ct1, mr1, metric), calcMI(ct2, mr2, metric))]
                
            
            
    # Calculate mean value for each metric
    for metric in metriclist:
        if len(patient_dic[patient_id].get(metric, [])) > 0:
            patient_dic[patient_id][metric].append(np.mean(patient_dic[patient_id][metric]))

if SAVE_AS_JSON:
    with open(os.path.join(utils.get_path("path_output"), "metric_MR_to_CT.json") , "w", encoding="utf-8") as f:
        json.dump(patient_dic, f, ensure_ascii=False, indent = 4)




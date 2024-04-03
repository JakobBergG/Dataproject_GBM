import os
import SimpleITK as sitk
import re
import math

def get_number(n):
    if n < 10:
        return "000" + str(n)
    if n < 100:
        return "00" + str(n)
    if n < 1000:
        return "0" + str(n)
    if n < 10000:
        return str(n)
    
path_data = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"
patient_folders = [f.path for f in os.scandir(path_data) if f.is_dir()]
no_patients = len(patient_folders)
# cut = 1
# Tr_patient_folders = patient_folders[:math.ceil(no_patients*cut)]
# Ts_patient_folders = patient_folders[math.ceil(no_patients*cut):]
Tr_patient_folders = patient_folders[:]
Ts_patient_folders = []


imagesTr_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\imagesTr"
imagesTs_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\imagesTs"
labelsTr_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\labelsTr"
labelsTs_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\labelsTs"


n = 1
bad_data = [] # ["4018", "4462", "4464"] # missing origonal brain mask file

# generate training data
for patient_folder in Tr_patient_folders:
    print(f"running on patient_folder {os.path.basename(patient_folder)} (Tr)")
    if os.path.basename(patient_folder) in bad_data:
        continue
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    for file in patient_filelist:
        if os.path.basename(file).endswith("stripped.nii.gz"):
            scan = sitk.ReadImage(file)
            imagesTr_output = os.path.join(imagesTr_output_path, "RGTV_" + get_number(n) + "_0000.nii.gz")
            print(imagesTr_output)
            sitk.WriteImage(scan, imagesTr_output)

        if os.path.basename(file).endswith("GTV.nii.gz"):
            scan = sitk.ReadImage(file)
            labelsTr_output = os.path.join(labelsTr_output_path, "RGTV_" + get_number(n) + ".nii.gz")
            print(labelsTr_output)
            sitk.WriteImage(scan, labelsTr_output)  
    n += 1

# generate test data
for patient_folder in Ts_patient_folders:
    print(f"running on patient_folder {os.path.basename(patient_folder)} (Ts)")
    if os.path.basename(patient_folder) in bad_data:
        continue
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    for file in patient_filelist:
        if os.path.basename(file).endswith("stripped.nii.gz"):
            scan = sitk.ReadImage(file)
            imagesTs_output = os.path.join(imagesTs_output_path, "RGTV_" + get_number(n) + "_0000.nii.gz")
            print(imagesTs_output)
            sitk.WriteImage(scan, imagesTs_output)
        if os.path.basename(file).endswith("GTV.nii.gz"):
            scan = sitk.ReadImage(file)
            labelsTs_output = os.path.join(labelsTs_output_path, "RGTV_" + get_number(n) + ".nii.gz")
            print(labelsTs_output)
            sitk.WriteImage(scan, labelsTs_output)
    n += 1

        
            


"""
import os
import SimpleITK as sitk
import re
import math

def get_number(n):
    if n < 10:
        return "000" + str(n)
    if n < 100:
        return "00" + str(n)
    if n < 1000:
        return "0" + str(n)
    if n < 10000:
        return str(n)
    
path_data = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"
patient_folders = [f.path for f in os.scandir(path_data) if f.is_dir()]
no_patients = len(patient_folders)
cut = 0.7
Tr_patient_folders = patient_folders[:math.ceil(no_patients*cut)]
Ts_patient_folders = patient_folders[math.ceil(no_patients*cut):]

imagesTr_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\imagesTr"
imagesTs_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\imagesTs"
labelsTr_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\labelsTr"
labelsTs_output_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task804_GBM_RECURRENCE_GTV\\labelsTs"


n = 1
bad_data = ["4018", "4462", "4464"] # missing brain mask file

# generate training data
for patient_folder in Tr_patient_folders:
    print(f"running on patient_folder {os.path.basename(patient_folder)} (Tr)")
    if os.path.basename(patient_folder) in bad_data:
        continue
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    for file in patient_filelist:
        if os.path.basename(file).endswith("stripped.nii.gz"):
            scan = sitk.ReadImage(file)
            imagesTr_output = os.path.join(imagesTr_output_path, "RGTV_" + get_number(n) + "_0000.nii.gz")
            print(imagesTr_output)
            sitk.WriteImage(scan, imagesTr_output)

        if os.path.basename(file).endswith("GTV.nii.gz"):
            scan = sitk.ReadImage(file)
            labelsTr_output = os.path.join(labelsTr_output_path, "RGTV_" + get_number(n) + ".nii.gz")
            print(labelsTr_output)
            sitk.WriteImage(scan, labelsTr_output)  
    n += 1

# generate test data
for patient_folder in Ts_patient_folders:
    print(f"running on patient_folder {os.path.basename(patient_folder)} (Ts)")
    if os.path.basename(patient_folder) in bad_data:
        continue
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    for file in patient_filelist:
        if os.path.basename(file).endswith("stripped.nii.gz"):
            scan = sitk.ReadImage(file)
            imagesTs_output = os.path.join(imagesTs_output_path, "RGTV_" + get_number(n) + "_0000.nii.gz")
            print(imagesTs_output)
            sitk.WriteImage(scan, imagesTs_output)
        if os.path.basename(file).endswith("GTV.nii.gz"):
            scan = sitk.ReadImage(file)
            labelsTs_output = os.path.join(labelsTs_output_path, "RGTV_" + get_number(n) + ".nii.gz")
            print(labelsTs_output)
            sitk.WriteImage(scan, labelsTs_output)
    n += 1
"""
        
            


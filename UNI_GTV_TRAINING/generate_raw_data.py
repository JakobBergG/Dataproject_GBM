import os
import re
import shutil
import random
import math
import SimpleITK as sitk


def get_number(n):
    # makes the number a 4 digit string
    if n < 10:
        return "000" + str(n)
    if n < 100:
        return "00" + str(n)
    if n < 1000:
        return "0" + str(n)
    if n < 10000:
        return str(n)


#First symlinks to anouks (Task666 in nnunet raw data) is created with same test/training split as in task 666 (digit 1 as the first digit)

#- fist the training images symlinks are created

task666_images_tr_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task666_editGTV\\imagesTr"
images_tr_folder_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task805_COMBINED_GBM\\imagesTr"
images_tr = [f.path for f in os.scandir(task666_images_tr_path)]


for image in images_tr:
    patient_number = re.findall(r'\d+', os.path.basename(image))[0]
    patient_number = get_number(int(patient_number))
    new_basename = f"ANOUK_1{patient_number}_0000.nii.gz" # there will be a 1 as the first digit because this is the special anouk data (must have same split as in task666 and the same patients are also found in the AUH data folder but theese will have 0 as the first digit)
    os.symlink(image, os.path.join(images_tr_folder_path, new_basename))

#- next the test images symlinks are created
    
task666_images_ts_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task666_editGTV\\imagesTs"
images_ts_folder_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task805_COMBINED_GBM\\imagesTs"
images_ts = [f.path for f in os.scandir(task666_images_ts_path)]


for image in images_ts:
    patient_number = re.findall(r'\d+', os.path.basename(image))[0]
    patient_number = get_number(int(patient_number))
    new_basename = f"ANOUK_1{patient_number}_0000.nii.gz" # there will be a 1 as the first digit because this is the special anouk data (must have same split as in task666 and the same patients are also found in the AUH data folder but theese will have 0 as the first digit)
    os.symlink(image, os.path.join(images_ts_folder_path, new_basename))

# next the training label symlinks are created

task666_labels_tr_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task666_editGTV\\labelsTr"
labels_tr_folder_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task805_COMBINED_GBM\\labelsTr"
labels_tr = [f.path for f in os.scandir(task666_labels_tr_path)]


for label in labels_tr:
    patient_number = re.findall(r'\d+', os.path.basename(label))[0]
    patient_number = get_number(int(patient_number))
    new_basename = f"ANOUK_1{patient_number}.nii.gz" # there will be a 1 as the first digit because this is the special anouk data (must have same split as in task666 and the same patients are also found in the AUH data folder but theese will have 0 as the first digit)
    os.symlink(label, os.path.join(labels_tr_folder_path, new_basename))

# next the test label symlinks are created

task666_labels_ts_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task666_editGTV\\labelsTs"
labels_ts_folder_path = "E:\\Jasper\\nnUNet\\nnUNet_raw_data\\Task805_COMBINED_GBM\\labelsTs"
labels_ts = [f.path for f in os.scandir(task666_labels_ts_path)]


for label in labels_ts:
    patient_number = re.findall(r'\d+', os.path.basename(label))[0]
    patient_number = get_number(int(patient_number))
    new_basename = f"ANOUK_1{patient_number}.nii.gz" # there will be a 1 as the first digit because this is the special anouk data (must have same split as in task666 and the same patients are also found in the AUH data folder but theese will have 0 as the first digit)
    os.symlink(label, os.path.join(labels_ts_folder_path, new_basename))




# now create symlinks for the hospitals (digit 0 as the first digit)
hospitals = ["AUH", "OUH", "CUH"]
cut = 0.8
for hospital in hospitals:
    hospital_data_path = os.path.join("D:\\GBM\\uni_gtv_tr_data", hospital)
    patient_files = [f.path for f in os.scandir(hospital_data_path)]
    random.shuffle(patient_files)
    
    # training files
    for patient_file in patient_files[:round(len(patient_files) * cut)]:
        patient_number = os.path.basename(patient_file)
        # image symlink
        new_basename = f"{hospital}_0{get_number(int(patient_number))}_0000.nii.gz"
        os.symlink(os.path.join(patient_file, f"{patient_number}_stripped_resliced.nii.gz"), os.path.join(images_tr_folder_path, new_basename))
        # label symlink
        new_basename = f"{hospital}_0{get_number(int(patient_number))}.nii.gz"
        os.symlink(os.path.join(patient_file, f"{patient_number}_gtv.nii.gz"), os.path.join(labels_tr_folder_path, new_basename))

    # test files
    for patient_file in patient_files[round(len(patient_files) * cut):]:
        patient_number = os.path.basename(patient_file)
        # image symlink
        new_basename = f"{hospital}_0{get_number(int(patient_number))}_0000.nii.gz"
        os.symlink(os.path.join(patient_file, f"{patient_number}_stripped_resliced.nii.gz"), os.path.join(images_ts_folder_path, new_basename))
        # label symlink
        new_basename = f"{hospital}_0{get_number(int(patient_number))}.nii.gz"
        os.symlink(os.path.join(patient_file, f"{patient_number}_gtv.nii.gz"), os.path.join(labels_ts_folder_path, new_basename))


# now create symlinks for the recurrence scans (digit 2 as the first digit)
recurrence_data_path = "D:\\GBM\\uni_gtv_tr_data\\RECURRENCE"
patient_files = [f.path for f in os.scandir(recurrence_data_path)]
random.shuffle(patient_files)

# training data
for patient_file in patient_files[:round(len(patient_files) * cut)]:
    patient_number = os.path.basename(patient_file)
    # image symlink
    new_basename = f"RECURRENCE_2{get_number(int(patient_number))}_0000.nii.gz"
    os.symlink(os.path.join(patient_file, f"{patient_number}_stripped_resliced.nii.gz"), os.path.join(images_tr_folder_path, new_basename))
    # label symlink
    new_basename = f"RECURRENCE_2{get_number(int(patient_number))}.nii.gz"
    os.symlink(os.path.join(patient_file, f"{patient_number}_gtv.nii.gz"), os.path.join(labels_tr_folder_path, new_basename))



for patient_file in patient_files[round(len(patient_files) * cut):]:
    patient_number = os.path.basename(patient_file)
    # image symlink
    new_basename = f"RECURRENCE_2{get_number(int(patient_number))}_0000.nii.gz"
    os.symlink(os.path.join(patient_file, f"{patient_number}_stripped_resliced.nii.gz"), os.path.join(images_ts_folder_path, new_basename))
    # label symlink
    new_basename = f"RECURRENCE_2{get_number(int(patient_number))}.nii.gz"
    os.symlink(os.path.join(patient_file, f"{patient_number}_gtv.nii.gz"), os.path.join(labels_ts_folder_path, new_basename))

















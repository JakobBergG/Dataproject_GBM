import os
import SimpleITK as sitk
import re

# NOTe THAT THE SAME TEST AND TRAINING SPLIT AS IN THE RECURRENCE_GBM TRAINING IS USED.


data_path = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"

patient_folders = [f.path for f in os.scandir(data_path) if f.is_dir()]

for patient_folder in patient_folders:
    try:
        patient_number = os.path.basename(patient_folder)
        patient_data = [f.path for f in os.scandir(patient_folder)]
        mask_path = [f.path for f in os.scandir(os.path.join(patient_folder, "brain_mr", "output_brains")) if f.path.endswith("MR_res_mask.nii.gz")][0]
        gtv_path = [f for f in patient_data if f.endswith("GTV.nii.gz")][0]
        
        # read images
        gtv = sitk.ReadImage(gtv_path)
        mask = sitk.ReadImage(mask_path)
        
        # combine gtv and mask
        or_filter = sitk.OrImageFilter()

        combined = or_filter.Execute(mask, gtv)
        
        # now dialate?
        dilate_filter = sitk.BinaryDilateImageFilter()

        dilate_filter.SetKernelType(sitk.sitkBall)

        # note voxels are (0.5, 0.5, 1)
        dilate_filter.SetKernelRadius((10,10,5))

        dilate_filter.SetForegroundValue(1)

        dialated_mask = dilate_filter.Execute(combined)

        dialated_mask_name = re.sub("GTV.nii.gz", "mask_dialated.nii.gz", os.path.basename(gtv_path))
        sitk.WriteImage(dialated_mask, os.path.join(patient_folder, dialated_mask_name))
        print(dialated_mask_name)

        # fin the MR scan

        scan_path = [f.path for f in os.scandir(patient_folder) if f.path.endswith("_MR.nii.gz")][0]
        scan = sitk.ReadImage(scan_path)

        # strip the MR scan
        stripped_dialated = sitk.Mask(scan, dialated_mask)

        stripped_dialated_name = re.sub("GTV.nii.gz", "stripped_dialated.nii.gz", os.path.basename(gtv_path))
        sitk.WriteImage(stripped_dialated, os.path.join(patient_folder, stripped_dialated_name))
    except Exception as e:
        print(e)



# loop through the files in the raw data for RECURRENCE GBM

# generate the dialated imagesTr files
imagesTr_path = "E:/Jasper/nnUNet/nnUNet_raw_data/Task808_RECURRENCE_GBM/imagesTr"
imagesTr_files = [f.path for f in os.scandir(imagesTr_path)]

for Tr_file in imagesTr_files:
    patient_number = os.path.basename(Tr_file)[12:16]
    
    # search for the corresponding file in the stripped_recurrence folder

    folder_to_search = os.path.join("C:/Users/Student1/Desktop/stripped_recurrence", patient_number)

    try:
        corresponding_file = [f.path for f in os.scandir(folder_to_search) if "MR_stripped_dialated" in os.path.basename(f.path)][0]
    except Exception as e:
        print(f"could not find corresponding file for patient {patient_number}")
        continue


    new_file_dest = os.path.join("E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/imagesTr", "RECURRENCE_2" + patient_number + "_0000.nii.gz")
    os.symlink(corresponding_file, new_file_dest)


# generate the dialated imagesTs files
imagesTs_path = "E:/Jasper/nnUNet/nnUNet_raw_data/Task808_RECURRENCE_GBM/imagesTs"
imagesTs_files = [f.path for f in os.scandir(imagesTs_path)]

for Ts_file in imagesTs_files:
    patient_number = os.path.basename(Ts_file)[12:16]
    
    # search for the corresponding file in the stripped_recurrence folder

    folder_to_search = os.path.join("C:/Users/Student1/Desktop/stripped_recurrence", patient_number)

    try:
        corresponding_file = [f.path for f in os.scandir(folder_to_search) if "MR_stripped_dialated" in os.path.basename(f.path)][0]
    except Exception as e:  
        print(f"could not find corresponding file for patient {patient_number}")
        continue


    new_file_dest = os.path.join("E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/imagesTs", "RECURRENCE_2" + patient_number + "_0000.nii.gz")
    os.symlink(corresponding_file, new_file_dest)   






#####################
# The below labels are used in the task: Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM
# Note that these labels have not been resliced.
#####################
    

# generate the dialated labelsTs files
labelsTr_path = "E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/labelsTr"
labelsTr_files = [f.path for f in os.scandir(labelsTr_path)]

for Tr_file in labelsTr_files:
    patient_number = os.path.basename(Tr_file)[12:16]
    
    # search for the corresponding file in the recurrence folder

    folder_to_search = "D:/GBM/recurrence/Cavity_excluded"

    try:
        corresponding_file = [f.path for f in os.scandir(folder_to_search) if os.path.basename(f.path).startswith(patient_number)][0]
    except Exception as e:  
        print(f"could not find corresponding file for patient {patient_number}")
        continue


    new_file_dest = os.path.join("E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/labelsTrTemp", "RECURRENCE_2" + patient_number + ".nii.gz")
    os.symlink(corresponding_file, new_file_dest)



# generate the dialated labelsTs files
labelsTs_path = "E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/labelsTs"
labelsTs_files = [f.path for f in os.scandir(labelsTs_path)]

for Ts_file in labelsTs_files:
    patient_number = os.path.basename(Ts_file)[12:16]
    
    # search for the corresponding file in the recurrence folder

    folder_to_search = "D:/GBM/recurrence/Cavity_excluded"

    try:
        corresponding_file = [f.path for f in os.scandir(folder_to_search) if os.path.basename(f.path).startswith(patient_number)][0]
    except Exception as e:  
        print(f"could not find corresponding file for patient {patient_number}")
        continue


    new_file_dest = os.path.join("E:/Jasper/nnUNet/nnUNet_raw_data/Task810_RECURRENCE_DIALATED_GBM/labelsTsTemp", "RECURRENCE_2" + patient_number + ".nii.gz")
    os.symlink(corresponding_file, new_file_dest)


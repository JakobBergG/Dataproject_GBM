import os
import SimpleITK as sitk
import re
import shutil

hospitals = ["AUH", "OUH", "CUH"]
label_base_path = "D:\\GBM\\nii"
training_base_path = "C:\\Users\\Student1\\Desktop\\temp_hospitals"
for hospital in hospitals:
    label_folders_path = os.path.join(label_base_path, hospital)
    # get list of label folders
    label_folders = [f.path for f in os.scandir(label_folders_path) if f.is_dir()]
    # work on one patient at a time
    for label_folder in label_folders:
        
        patient_number = os.path.basename(label_folder)

        # see if label exists
        try:
            ct_path = [f.path for f in os.scandir(label_folder) if f.path.endswith("CT")][0]
            label_path = [f.path for f in os.scandir(os.path.join(ct_path, "RTSTRUCTS_0")) if os.path.basename(f) == "gtv.nii.gz"][0]

        except Exception as e:
            print(f"could not get label for patient {patient_number}: {e}")
            continue
    
        # now we are left with an existing label for the patient.
        # now search for patient in the output folder (training input)

        # get the training MR
        try:
            # First get stripped file:
            stripped_file_path = f"{training_base_path}\\{hospital}\\{patient_number}\\brain_mr\\output_brains\\{patient_number}_MR_res_stripped.nii.gz" 
            mask_file_path = f"{training_base_path}\\{hospital}\\{patient_number}\\brain_mr\\output_brains\\{patient_number}_MR_res_mask_cleaned.nii.gz" 
            if not os.path.exists(stripped_file_path):
                print(f"could not get stripped_file path for patient {patient_number}")
                continue
            if not os.path.exists(mask_file_path):
                print(f"could not get mask_file_path for patient {patient_number}")
                continue
            hospital_folder_path = os.path.join("D:\\GBM\\uni_gtv_tr_data", hospital)
            if not os.path.exists(hospital_folder_path):
                os.mkdir(hospital_folder_path)
            patient_folder_path = os.path.join(hospital_folder_path, patient_number)
            if not os.path.exists(patient_folder_path):
                os.mkdir(patient_folder_path)
            new_stripped_file_path = os.path.join(patient_folder_path, f"{patient_number}_stripped.nii.gz")
            new_mask_file_path = os.path.join(patient_folder_path, f"{patient_number}_mask.nii.gz")                   
            shutil.copyfile(stripped_file_path, new_stripped_file_path)
            shutil.copyfile(mask_file_path, new_mask_file_path)
        except Exception as e:
            print(f"could not get training file for patient {patient_number}: {e}")
            continue
        try:
            # generate symlink for label
            label_dest = os.path.join(patient_folder_path, f"{patient_number}_gtv.nii.gz")
            os.symlink(label_path, label_dest) 
        except Exception as e:
            print(f"could not get label for patient {patient_number}: {e}")
            continue
        

     



# def run(i, j):
#     hospitals = ["AUH", "OUH", "CUH"]
#     label_base_path = "D:\\GBM\\nii"
#     training_base_path = "D:\GBM\output"
#     for hospital in hospitals[i: i+1]:
#         label_folders_path = os.path.join(label_base_path, hospital)
#         # get list of label folders
#         label_folders = [f.path for f in os.scandir(label_folders_path) if f.is_dir()]
#         # work on one patient at a time
#         for label_folder in label_folders[j:j+1]:
#             patient_number = os.path.basename(label_folder)

#             # see if label exists
#             try:
#                 ct_path = [f.path for f in os.scandir(label_folder) if f.path.endswith("CT")][0]
#                 label_path = [f.path for f in os.scandir(os.path.join(ct_path, "RTSTRUCTS_0")) if os.path.basename(f) == "gtv.nii.gz"][0]
                
#             except Exception as e:
#                 print(f"could not get label for patient {patient_number}: {e}")
#                 continue
        
#             # now we are left with an existing label for the patient.
#             # now search for patient in the output folder (training input)

#             # get the training MR
#             try:
#                 # first determine the time2 MR file by searching in the summary file
#                 t2_files_path = f"D:\\GBM\\summary\\{hospital}\\{patient_number}"
#                 # if t2_file_path cant be found this will give an error since there will be an empty list
#                 t2_file_path = [f.path for f in os.scandir(t2_files_path) if os.path.basename(f.path).startswith("time2") and f.path.endswith("MR.nii.gz")][0]
#                 # now retrieve the t2 file to search for in the output folder
#                 training_MR_file_name = re.sub("time2_", "", os.path.basename(t2_file_path))
#                 print(f"training_mr_file_name: {training_MR_file_name}")

#                 training_files_path = os.path.join(training_base_path, hospital, patient_number, "MR_TO_CT_mask")
#                 training_MR_file = [f.path for f in os.scandir(training_files_path) if os.path.basename(f.path) == training_MR_file_name][0]
#             except Exception as e:
#                 print(f"could not get training file for patient {patient_number}: {e}")
#                 continue
            
#             # get the training MR mask
#             try:
#                 training_mask_file_name = re.sub(".nii.gz", "_mask.nii.gz", training_MR_file_name)
#                 training_mask_file = [f.path for f in os.scandir(training_files_path) if f.path.endswith(training_mask_file_name)][0]
#             except Exception as e:
#                 print(f"could not get training mask for patient {patient_number}: {e}")
#                 continue

#             # get the stripped training image
#             try:
#                 hospital_folder_path = os.path.join("D:\\GBM\\uni_gtv_tr_data", hospital)
#                 if not os.path.exists(hospital_folder_path):
#                     os.mkdir(hospital_folder_path)
#                 patient_folder_path = os.path.join(hospital_folder_path, patient_number)
#                 if not os.path.exists(patient_folder_path):
#                     os.mkdir(patient_folder_path)
                
#                 # save training file
#                 scan = sitk.ReadImage(training_MR_file)
#                 mask = sitk.ReadImage(training_mask_file)
                
#                 stripped_skull = sitk.Mask(scan, mask)

#                 sitk.WriteImage(stripped_skull, os.path.join(patient_folder_path, f"{patient_number}_stripped.nii.gz"))

#                 # create symbolic link to label file (the gtv segmentation)
#                 label_dest = os.path.join(patient_folder_path, f"{patient_number}_gtv.nii.gz")
#                 os.symlink(label_path, label_dest)            
#             except Exception as e:
#                 print(patient_number)
#                 print(f"test: {e}")

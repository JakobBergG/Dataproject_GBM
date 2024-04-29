import os
import SimpleITK as sitk
import re

hospitals = ["AUH", "OUH", "CUH"]
label_base_path = "D:\\GBM\\nii"
training_base_path = "D:\GBM\output"
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
            # first determine the time2 MR file by searching in the summary file
            t2_files_path = f"D:\\GBM\\summary\\{hospital}\\{patient_number}"
            # if t2_file_path cant be found this will give an error since there will be an empty list
            t2_file_path = [f.path for f in os.scandir(t2_files_path) if os.path.basename(f.path).startswith("time2") and f.path.endswith("MR.nii.gz")][0]
            # now retrieve the t2 file to search for in the output folder
            training_MR_file_name = re.sub("time2_", "", os.path.basename(t2_file_path))
            print(f"training_mr_file_name: {training_MR_file_name}")

            training_files_path = os.path.join(training_base_path, hospital, patient_number, "MR_TO_CT_mask")
            training_MR_file = [f.path for f in os.scandir(training_files_path) if os.path.basename(f.path) == training_MR_file_name][0]
        except Exception as e:
            print(f"could not get training file for patient {patient_number}: {e}")
            continue
        
        # get the training MR mask
        try:
            training_mask_file_name = re.sub(".nii.gz", "_mask.nii.gz", training_MR_file_name)
            training_mask_file = [f.path for f in os.scandir(training_files_path) if f.path.endswith(training_mask_file_name)][0]
        except Exception as e:
            print(f"could not get training mask for patient {patient_number}: {e}")
            continue

        # create symlink to tempary folder
        try:
            hospital_folder_path = os.path.join("C:\\Users\\Student1\\Desktop\\temp_hospitals", hospital)
            if not os.path.exists(hospital_folder_path):
                os.mkdir(hospital_folder_path)
            patient_folder_path = os.path.join(hospital_folder_path, patient_number)
            if not os.path.exists(patient_folder_path):
                os.mkdir(patient_folder_path)

            scan_dest = os.path.join(patient_folder_path, f"{patient_number}_MR.nii.gz")
            os.symlink(training_MR_file, scan_dest) 
            print(f"done for patient {patient_number}")           
        except Exception as e:
            print(patient_number)
            print(f"test: {e}")



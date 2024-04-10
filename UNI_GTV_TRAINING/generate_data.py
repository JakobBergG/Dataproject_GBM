import os
import SimpleITK as sitk
import re


hospitals = ["AUH", "OUH", "CUH"]
label_base_path = "D:\\GBM\\nii"
training_base_path = "D:\GBM\output_test"
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
    
        # now we are left with a existing label for the patient.
        # now search for patient in the output folder (training input)

        # get the training MR
        try:
            training_files_path = os.path.join(training_base_path, hospital, patient_number, "MR_TO_CT_mask")
            training_MR_files = [f.path for f in os.scandir(training_files_path) if f.path.endswith("MR.nii.gz")]
            training_MR_file = min(training_MR_files)
        except Exception as e:
            print(f"could not get training file for patient {patient_number}: {e}")
            continue
        
        # get the training MR mask
        try:
            training_mask_files = [f.path for f in os.scandir(training_files_path) if f.path.endswith("mask.nii.gz")]
            training_mask_file = min(training_mask_files)
        except Exception as e:
            print(f"could not get training mask for patient {patient_number}: {e}")
            continue

        # get the stripped training image
        try:
            hospital_folder_path = os.path.join("D:\\GBM\\uni_gtv_tr_data", hospital)
            if not os.path.exists(hospital_folder_path):
                os.mkdir(hospital_folder_path)
            patient_folder_path = os.path.join(hospital_folder_path, patient_number)
            if not os.path.exists(patient_folder_path):
                os.mkdir(patient_folder_path)
            output_training_path = os.path.join(patient_folder_path, "training")
            output_label_path = os.path.join(patient_folder_path, "label")
            if not os.path.exists(output_training_path):
                os.mkdir(output_training_path)
            if not os.path.exists(output_label_path):
                os.mkdir(output_label_path)

            # save training file
            scan = sitk.ReadImage(training_MR_file)
            mask = sitk.ReadImage(training_mask_file)
            stripped_skull = sitk.Mask(scan, mask, toler)
            sitk.WriteImage(stripped_skull, os.path.join(output_training_path, f"{patient_number}_stripped.nii.gz"))

            
        except Exception as e:
            print(patient_number)
            print(f"test: {e}")


import os
data_path = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"

patient_folders = [f.path for f in os.scandir(data_path) if f.is_dir()]

for patient_folder in patient_folders:
    try:
        patient_number = os.path.basename(patient_folder)
        patient_data = [f.path for f in os.scandir(patient_folder)]
        label = [f for f in patient_data if f.endswith("GTV.nii.gz")][0]
        stripped = [f for f in patient_data if f.endswith("stripped.nii.gz")][0]
        hospital_folder_path = "D:\\GBM\\uni_gtv_tr_data\\RECURRENCE"
        if not os.path.exists(hospital_folder_path):
            os.mkdir(hospital_folder_path)
        patient_folder_path = os.path.join(hospital_folder_path, patient_number)
        if not os.path.exists(patient_folder_path):
            os.mkdir(patient_folder_path)   
        label_dest = os.path.join(patient_folder_path, f"{patient_number}_gtv.nii.gz")
        os.symlink(label, label_dest)
        stripped_dest = os.path.join(patient_folder_path, f"{patient_number}_stripped.nii.gz")
        os.symlink(stripped, stripped_dest)
    except Exception as e:
        print(e)
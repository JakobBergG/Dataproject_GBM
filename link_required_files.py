import os

input_folder = "../nii_preprocessed"
output_folder = "../pipeline_input"

endings_to_copy = [
    "_MR_res.nii.gz",
    "_CT_res.nii.gz",
    "_RTDOSE_res.nii.gz"
]

input_patient_folders = [f.path for f in os.scandir(input_folder) if f.is_dir()]

for patient_input_folder in input_patient_folders:
    # setup input and output folders
    patient_id = os.path.basename(patient_input_folder)
    output_patient_folder = os.path.join(output_folder, patient_id)
    if not os.path.isdir(output_patient_folder):
        os.mkdir(output_patient_folder)
    
    # now move the needed scans
    input_files = [f.path for f in os.scandir(patient_input_folder) if f.is_file]
    for input_file in input_files:
        file_name = os.path.basename(input_file)
        for ending in endings_to_copy:
            if file_name.endswith(ending):
                
                # then create link to the file
                output_file = os.path.join(output_patient_folder, file_name)
                if not os.path.exists(output_file):
                    input_full_path = os.path.abspath(input_file)
                    os.symlink(input_full_path, output_file)

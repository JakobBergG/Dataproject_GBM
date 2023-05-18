'''
This is a simple scan for counting the number of scans
'''

import os
import common.utils as utils

basepath = utils.get_path("path_data")
patient_folders = [f.path for f in os.scandir(basepath) if f.is_dir()]

n_ct = 0
n_mr = 0
n_rtdose = 0
n_patient = 0

endings_to_consider = [
    "_MR_res.nii.gz",
    "_CT_res.nii.gz",
    "_RTDOSE_res.nii.gz"
]


for patient_folder in patient_folders:
    n_patient += 1
    files = [f.path for f in os.scandir(patient_folder) if f.is_file]
    for file in files:
        file_name = os.path.basename(files)
        if file_name.endswith("_MR_res.nii.gz"):
            n_mr += 1
        elif file_name.endswith("_CT_res.nii.gz"):
            n_ct += 1
        if file_name.endswith("_RTDOSE_res.nii.gz"):
            n_rtdose += 1


print("Number of patients:", n_patient)
print("Number of MR scans:", n_mr)
print("Number of CT scans:", n_ct)
print("Number of RTDOSE:", n_rtdose)
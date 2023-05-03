import json
import common.utils as utils
import os

output_path = os.path.join(utils.get_path("path_output"), "registration_mask_MSD_2023-04-28_11-49-34")

with open(output_path, "r") as f:
    patient_dic : dict = json.load(f)

# Sort patient dictionary by average MSD
sorted_patients = sorted(patient_dic.items(), key = lambda L: L[1][-1])
patient_dic = {key : value for key, value in sorted_patients}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(patient_dic, f, ensure_ascii=False, indent = 4)
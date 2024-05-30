import csv
import os
import json
"""
Script to find scans that are both classified by Anouk (local vs not local recurrence) 
and have viable MR scans and brain mask after going through the pipeline.
 
"""
JOURNAL_PATH = "D:/GBM/radiomic_results/overview_with_combined.csv"

# LOAD TUMOR CLASS #
journal_info_patients = set()
with open(JOURNAL_PATH, newline='', mode="r", encoding="utf-8-sig") as f:
    rows = csv.reader(f, delimiter=",")
    names = next(rows) # The first row gives the names of the columns
    
    # Now read info for all patients
    for row in rows:
        if row[2] == "local_distant":
            study_id = f"{row[1]:>04}" # Pad with 4 zeros
            journal_info_patients.add(study_id)

print("Number of scans Anouk has classified", len(journal_info_patients))

# PATIENTS WITH VIABLE SCANS # 
hospitals = ["AUH", "OUH", "CUH"]
datapath = "D:\\GBM\\uni_gtv_tr_data\\"

available_patients_data = set()
for hospital in hospitals:
    available_patients_data.update(os.listdir(datapath + hospital))

print("Number of available MR scans are:", len(available_patients_data))

# FIND VIABLE PATIENTS BY INTERSECTION #
intersection = journal_info_patients.intersection(available_patients_data)

print("Patients in common:", len(intersection))

with open("D:\\GBM\\radiomic_results\\available_patients_time2_combined.json", "w") as f:
    json.dump(list(intersection), f)
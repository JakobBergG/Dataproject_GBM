import csv
import json

# Study_ID: 0, TumorLabel: 1, TumorClass: 2 
journal_path = "D:\\GBM\output_test\\radiomic_results\\tumorlabels.csv"
all_radiomic_features_path = "D:\\GBM\output_test\\radiomic_results"

journal_info_patients = {}

with open(journal_path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns
        
        # Now read info for all patients
        for row in rows:
            Tumor_class = int(row[2])
            study_id = f"{row[0]:>04}" # Pad with 4 zeros
            journal_info_patients[study_id] = Tumor_class

for id, cls in journal_info_patients.items():
    print(id)

print("\",\"".join((id) for id, cls in journal_info_patients.items()))
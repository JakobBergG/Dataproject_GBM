import csv
import json

journal_path = "D:\\GBM\\radiomic_results\\overview_with_combined.csv"
all_radiomic_features_path = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_all_classes.json"

# LOAD TUMOR CLASS #
journal_info_patients = {}
with open(journal_path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns
        
        # Now read info for all patients
        for row in rows:
            tumor_class = int(row[3])
            study_id = f"{row[1]:>04}" # Pad with 4 zeros
            journal_info_patients[study_id] = tumor_class

# LOAD RADIOMIC FEATURES #
with open(all_radiomic_features_path) as f:
    all_radiomic_features = json.load(f)

# COMBINE #
patient_info = {}
for patient, features in all_radiomic_features.items():
    patient_info[patient] = {"tumor_class": journal_info_patients[patient],
                             "features": features} # features is also a Dict
    

for patient, features in all_radiomic_features.items():
    if features["original_firstorder_Minimum"] < 0:
         print(patient, features["original_firstorder_Minimum"])
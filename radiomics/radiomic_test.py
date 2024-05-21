import csv

JOURNAL_PATH = "D:/GBM/radiomic_results/overview.csv"

# LOAD TUMOR CLASS #
journal_info_patients = set()
with open(JOURNAL_PATH, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns
        
        # Now read info for all patients
        for row in rows:
            study_id = f"{row[1]:>04}" # Pad with 4 zeros
            journal_info_patients.add(study_id)

print(len(journal_info_patients))

available_patients_data = set()
hospitals = 
"D:\\GBM\\uni_gtv_tr_data"
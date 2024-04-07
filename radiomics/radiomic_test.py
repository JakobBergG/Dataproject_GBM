import csv
import json

available_patients = []
journal_path = "D:\\GBM\output_test\\radiomic_results\\tumorlabels.csv"
with open(journal_path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns

        for id, _, _ in rows:
             available_patients.append(f"{str(id):>04}")

with open("D:\\GBM\output_test\\radiomic_results\\available_patients.json", "w") as f:
    json.dump(available_patients, f)
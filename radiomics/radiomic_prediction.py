import csv
import json
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import numpy as np

# Study_ID: 0, TumorLabel: 1, TumorClass: 2 
journal_path = "D:\\GBM\output_test\\radiomic_results\\tumorlabels.csv"
all_radiomic_features_path = "D:\\GBM\output_test\\radiomic_results\\patient_features.json"

# LOAD TUMOR CLASS #
journal_info_patients = {}
with open(journal_path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns
        
        # Now read info for all patients
        for row in rows:
            Tumor_class = int(row[2])
            study_id = f"{row[0]:>04}" # Pad with 4 zeros
            journal_info_patients[study_id] = Tumor_class

# LOAD RADIOMIC FEATURES #
with open(all_radiomic_features_path) as f:
    all_radiomic_features = json.load(f)

# COMBINE #
# Some of the patients from the csv raised error when calculating features. (e.g. missing images, non-existent mask)
# Valid patients only if they are present in csv and have valid radiomic features.
patient_info = {}
for patient, features in all_radiomic_features.items():
    patient_info[patient] = {"TumorClass": journal_info_patients[patient],
                             "features": features} # features is a Dict

# PRINT FEATURE DIFFERENCES - OPTIONAL #
do_print = False
if do_print:
    feature_list_cls1 = []
    feature_list_cls2 = []
    for patient, info in patient_info.items():
        if info["TumorClass"] == 1:
            feature_list_cls1.append([value for feature, value in info["features"].items()])
        if info["TumorClass"] == 2:
            feature_list_cls2.append([value for feature, value in info["features"].items()])

    feature_list_cls1 = np.array(feature_list_cls1).T
    feature_list_cls2 = np.array(feature_list_cls2).T

    fig, axs = plt.subplots(3,2)
    for i in range(3):
        axs[i,0].boxplot(feature_list_cls1[i])
        axs[i,0].grid(axis="y")

        axs[i,1].boxplot(feature_list_cls2[i])
        axs[i,1].grid(axis="y")
        axs[i,1].sharey(axs[i,0])
    plt.show()

# SET UP DATAFRAME FOR REGRESSION #
# FIT LOGISTIC REGRESSION #
# I tried to get a balanced amount of local and distant recurrence. However something is majorly wrong:
# Include all local recurrences = classifier predicts only local recurrence
# Make it 50/50 local/distant = classifier guesses 50% correct.
# Consider checking:
# - Are masks correct?
# - Actually following the article correctly. (It uses the ring around the tumor instead of the GTV itself, but I don't know how to do that)

X = []
y = []
myCounter = 0
for patient, info in patient_info.items():
    if info["TumorClass"] != 3:
        if myCounter == 23 and info["TumorClass"] == 1:
            continue
        X.append([value for _, value in info["features"].items()])
        y.append(info["TumorClass"])
        if info["TumorClass"] == 1:
            myCounter += 1
        
        

clf = LogisticRegression().fit(X,y)

print(sum(clf.predict(X) == y) / len(y))
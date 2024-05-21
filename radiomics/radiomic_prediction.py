import csv
import json
from sklearn.ensemble import AdaBoostClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, cross_validate
import itertools
from imblearn.under_sampling import RandomUnderSampler

# Study_ID: 0, TumorLabel: 1, TumorClass: 2 
journal_path = "D:\\GBM\\radiomic_results\\time0 resources\\tumorlabels_AUH.csv"
all_radiomic_features_path = "D:\\GBM\\radiomic_results\\time0 resources\\patient_all_features.json"

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
# Some of the patients from the csv raised error when calculating radiomic features. (e.g. missing images, non-existent mask)
# Valid patients only if they are PRESENT IN CSV and HAVE VALID RADIOMIC FEATURES.
patient_info = {}
for patient, features in all_radiomic_features.items():
    patient_info[patient] = {"TumorClass": journal_info_patients[patient]-1,
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

X = []
y = []
# myCounter = 100
# for patient, info in patient_info.items():
#     if info["TumorClass"] != 3:
#         if myCounter == 23 and info["TumorClass"] == 1:
#             continue
#         X.append([value for _, value in info["features"].items()])
#         y.append(info["TumorClass"])
#         if info["TumorClass"] == 1:
#             myCounter += 1
        
for patient, info in patient_info.items():
    if info["TumorClass"] != 2:
        X.append([value for _, value in info["features"].items()])
        y.append(info["TumorClass"])

def train_and_predict(X, y, total_amount_features = 3, use_combinations = False):

    rus = RandomUnderSampler(random_state=42)
    X, y = rus.fit_resample(X, y)

    if use_combinations == True:
        X = np.array(X)
        for features in range(1, min(3, total_amount_features)):
            #wack solution X[0], please re-write
            for subset in itertools.combinations(list(range(1, len(X[0]))), features):
                X_data = X[:, subset]

                clf = AdaBoostClassifier(algorithm="SAMME")

                X_train_test, X_val, y_train_test, y_val = train_test_split(X_data, y)
                scores = cross_val_score(clf, X_train_test, y_train_test)
                print(scores)

    else:

        clf = AdaBoostClassifier(algorithm="SAMME")

        X_train_test, X_val, y_train_test, y_val = train_test_split(X, y)

        #Change the code from here. Get the top features with the kfold 


        clf.fit(X, y)

        feature_importance = clf.feature_importances_

        for amount_features in range(1, total_amount_features):
            print("-------------")
            print(f"Currently using {amount_features} of features")

            clf = AdaBoostClassifier(algorithm="SAMME")

            top_indicies = np.argsort(feature_importance)[::-1][:amount_features]
            X_data = np.array(X)

            X_data= X_data[:, top_indicies]

            X_train_test, X_val, y_train_test, y_val = train_test_split(X_data, y)

            scores = cross_val_score(clf, X_train_test, y_train_test)
            print(scores.mean())

            print("Printing prediction scores")

            clf = AdaBoostClassifier(algorithm="SAMME")
            clf.fit(X_train_test, y_train_test)
            print(sum(clf.predict(X_val) == y_val) / len(y_val))
            print("-------------")




train_and_predict(X, y, total_amount_features=20, use_combinations=False)



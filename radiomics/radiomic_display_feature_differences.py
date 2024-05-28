import csv
import json
import matplotlib.pyplot as plt
import numpy as np
"""
Script to display a boxplot of the values of certain features for each class to compare their differences.


"""
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

# PRINTING #
do_print = False
included_features = ['original_shape_Flatness', 'original_firstorder_Minimum', 'original_gldm_SmallDependenceLowGrayLevelEmphasis'] # From own tests
# included_features = ["original_glcm_Contrast", "original_glcm_Correlation", "original_glrlm_RunLengthNonUniformity"] # From paper
if do_print:
    
    feature_list_cls0 = []
    feature_list_cls1 = []
    for feature in included_features:
        temp_cls0 = []
        temp_cls1 = []
        for patient, info in patient_info.items():
            if info["tumor_class"] == 0:
                temp_cls0.append(info["features"][feature])
            else:
                temp_cls1.append(info["features"][feature])

        feature_list_cls0.append(temp_cls0)
        feature_list_cls1.append(temp_cls1)

    fig, axs = plt.subplots(3,2)
    column_titles = ["Local", "Distant"]
    for ax, col_title in zip(axs[0], column_titles):
        ax.set_title(col_title)

    for ax, feature in zip(axs[:,0], included_features):
        ax.set_ylabel(feature, size="large")

    for i in range(3):
        axs[i,0].boxplot(feature_list_cls0[i])
        axs[i,0].grid(axis="y")

        axs[i,1].boxplot(feature_list_cls1[i])
        axs[i,1].grid(axis="y")
        axs[i,1].sharey(axs[i,0])
    plt.show()
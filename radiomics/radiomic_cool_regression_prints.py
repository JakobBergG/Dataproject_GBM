import csv
import json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import cross_val_score

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


# PRINT FEATURE DIFFERENCES - OPTIONAL #
do_print = False
included_features = ["original_glcm_Contrast", "original_glcm_Correlation", "original_glrlm_RunLengthNonUniformity"]
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
    for i in range(3):
        axs[i,0].title.set_text(included_features[i] + " Local")
        axs[i,0].boxplot(feature_list_cls0[i])
        axs[i,0].grid(axis="y")

        axs[i,1].title.set_text(included_features[i] + " Distant")
        axs[i,1].boxplot(feature_list_cls1[i])
        axs[i,1].grid(axis="y")
        axs[i,1].sharey(axs[i,0])
    plt.show()

# SET UP DATAFRAME FOR REGRESSION #
# FIT LOGISTIC REGRESSION #

X = []
y = []
for patient, info in patient_info.items():
    X.append([value for _, value in info["features"].items()])
    y.append(info["tumor_class"])

print("Total available scans:", len(X))

rus = RandomUnderSampler()
X, y = rus.fit_resample(X, y)

print("Available after undersampling:", len(X))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y)

clf = LogisticRegression(max_iter=1000)
# clf = AdaBoostClassifier(algorithm="SAMME")
clf.fit(X_train,y_train)


## Printing results
format_offset = 25
class header_col:
    TITLE = "\033[95m"
    SUBTITLE = "\033[92m"
    END = "\033[0m"


number_of_patients = len(y_train)
number_of_local = number_of_patients - sum(y_train)

print(header_col.TITLE + "*" * 6 + " TRAIN DATA MODEL " + "*" * 6 + header_col.END)
print(header_col.SUBTITLE + "*** MODEL INPUT ***" + header_col.END)
print("Local: ".ljust(format_offset, "-"), number_of_local)
print("Distant & Combined: ".ljust(format_offset, "-"), (number_of_patients - number_of_local))
print("Total scans: ".ljust(format_offset, "-"), number_of_patients)
print("% of total being local: ".ljust(format_offset, "-"), f"{number_of_local / number_of_patients * 100:.1f}%")

print(header_col.SUBTITLE + "\n*** MODEL PERFORMANCE ***" + header_col.END)
print("# of local guesses: ".ljust(format_offset, "-"), number_of_patients - sum(clf.predict(X_train)))
print("Accuracy: ".ljust(format_offset, "-"), f"{clf.score(X_train,y_train) * 100:.1f}%")


number_of_patients = len(y_test)
number_of_local = number_of_patients - sum(y_test)
print(header_col.TITLE + "\n" + "*" * 6 + " TEST DATA MODEL " + "*" * 6 + header_col.END)
print(header_col.SUBTITLE + "*** MODEL INPUT ***" + header_col.END)
print("Local: ".ljust(format_offset, "-"), number_of_local)
print("Distant & Combined: ".ljust(format_offset, "-"), (number_of_patients - number_of_local))
print("Total scans: ".ljust(format_offset, "-"), number_of_patients)
print("% of total being local: ".ljust(format_offset, "-"), f"{number_of_local / number_of_patients * 100:.1f}%")

print(header_col.SUBTITLE + "\n*** MODEL PERFORMANCE ***" + header_col.END)
print("# of local guesses: ".ljust(format_offset, "-"), number_of_patients - sum(clf.predict(X_test)))
print("Accuracy: ".ljust(format_offset, "-"), f"{clf.score(X_test,y_test) * 100:.1f}%")

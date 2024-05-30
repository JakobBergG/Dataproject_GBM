import csv
import json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
import matplotlib.pyplot as plt
import numpy as np

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
EQUAL_GROUPS = False
if EQUAL_GROUPS:
    myCounter = 0
    max_number_of_local = 115
    for patient, info in patient_info.items():
        cls = info["tumor_class"]
        if cls != 2:
            if myCounter == max_number_of_local and cls == 0:
                continue
            X.append([value for _, value in info["features"].items()])
            y.append(cls)
            if cls == 0:
                myCounter += 1
else:
    for patient, info in patient_info.items():
        if info["tumor_class"] != 2:
            X.append([value for _, value in info["features"].items()])
            y.append(info["tumor_class"])

data = zip(X, y)
test_set_size = 20
train = []
test = []

cls_counter = {
    0: 0,
    1: 0
}
for features, label in data:
    if cls_counter[label] < test_set_size:
        test.append((features, label))
        cls_counter[label] += 1
    else:
        train.append((features, label))

X, y = zip(*train)
clf = LogisticRegression()
clf.fit(X,y)

## Printing results
format_offset = 25
class header_col:
    TITLE = "\033[95m"
    SUBTITLE = "\033[92m"
    END = "\033[0m"


number_of_patients = len(y)
number_of_local = number_of_patients - sum(y)

print(header_col.TITLE + "*" * 6 + " TRAIN DATA MODEL " + "*" * 6 + header_col.END)
print(header_col.SUBTITLE + "*** MODEL INPUT ***" + header_col.END)
print("Local: ".ljust(format_offset, "-"), number_of_local)
print("Distant & Combined: ".ljust(format_offset, "-"), (number_of_patients - number_of_local))
print("Total scans: ".ljust(format_offset, "-"), number_of_patients)
print("% of total being local: ".ljust(format_offset, "-"), f"{number_of_local / number_of_patients * 100:.1f}%")

print(header_col.SUBTITLE + "\n*** MODEL PERFORMANCE ***" + header_col.END)
print("# of local guesses: ".ljust(format_offset, "-"), number_of_patients - sum(clf.predict(X)))
print("Accuracy: ".ljust(format_offset, "-"), f"{clf.score(X,y) * 100:.1f}%")

X, y = zip(*test)
number_of_patients = len(y)
number_of_local = number_of_patients - sum(y)
print(header_col.TITLE + "\n" + "*" * 6 + " TEST DATA MODEL " + "*" * 6 + header_col.END)
print(header_col.SUBTITLE + "*** MODEL INPUT ***" + header_col.END)
print("Local: ".ljust(format_offset, "-"), number_of_local)
print("Distant & Combined: ".ljust(format_offset, "-"), (number_of_patients - number_of_local))
print("Total scans: ".ljust(format_offset, "-"), number_of_patients)
print("% of total being local: ".ljust(format_offset, "-"), f"{number_of_local / number_of_patients * 100:.1f}%")

print(header_col.SUBTITLE + "\n*** MODEL PERFORMANCE ***" + header_col.END)
print("# of local guesses: ".ljust(format_offset, "-"), number_of_patients - sum(clf.predict(X)))
print("Accuracy: ".ljust(format_offset, "-"), f"{clf.score(X,y) * 100:.1f}%")

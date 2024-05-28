import csv
import json
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.model_selection import KFold
import itertools
from imblearn.under_sampling import RandomUnderSampler
from scipy.stats import mannwhitneyu, pearsonr

# Study_ID: 0, TumorLabel: 1, TumorClass: 2 
journal_path = "D:\\GBM\\radiomic_results\\overview_with_combined.csv"
all_radiomic_features_path = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_all_classes.json"

# LOAD TUMOR CLASS #
journal_info_patients = {}
with open(journal_path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=",")
        names = next(rows) # The first row gives the names of the columns
        
        # Now read info for all patients
        for row in rows:
            Tumor_class = int(row[3])
            study_id = f"{row[1]:>04}" # Pad with 4 zeros
            journal_info_patients[study_id] = Tumor_class

# LOAD RADIOMIC FEATURES #
with open(all_radiomic_features_path) as f:
    all_radiomic_features = json.load(f)

# COMBINE #
# Some of the patients from the csv raised error when calculating radiomic features. (e.g. missing images, non-existent mask)
# Valid patients only if they are PRESENT IN CSV and HAVE VALID RADIOMIC FEATURES.
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

    X, y = np.array(X), np.array(y)
    #Splitting the data into equal sizes of classes
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

                clf = AdaBoostClassifier(algorithm="SAMME")
                clf.fit(X_train_test, y_train_test)
                print(sum(clf.predict(X_val) == y_val) / len(y_val))

    else:

        clf = AdaBoostClassifier(algorithm="SAMME")

        kf  = KFold(n_splits=5)

        all_feature_importances = []

        accurary = []
        
        #splitting the features so we have some data to validate the features on
        X_train_test, X_val, y_train_test, y_val = train_test_split(X, y, random_state=42)

        for train_index, test_index in kf.split(X_train_test):

            print(train_index, test_index)
            #take the train data indicies and get it from the data
            X_train, X_test = X_train_test[train_index], X_train_test[test_index]
            y_train, y_test = y_train_test[train_index], y_train_test[test_index]

            clf.fit(X_train, y_train)
            
            #Get the most important features for that model
            feature_importances = clf.feature_importances_

            all_feature_importances.append(feature_importances)

            #append the accuracy
            accurary.append(sum(clf.predict(X_val)==y_val)/len(y_val))

        all_feature_importances = np.array(all_feature_importances)

        mean_feature_importances = np.mean(all_feature_importances, axis=0)

        #get the mean of the accuracy
        accurary = np.mean(accurary)

        sorted_features = np.argsort(mean_feature_importances)[::-1]

        print(sorted_features)
        print(accurary)

        for i in range(1, min(len(sorted_features), 10)):
            print("-------------")
            print(f"Currently using {i} of features")

            clf = AdaBoostClassifier(algorithm="SAMME")

            #Get the top indicies that we want
            top_indicies = sorted_features[:i]
            X_data = np.array(X)

            X_data= X_data[:, top_indicies]

            #Split the data into train+test and val
            X_train_test, X_val, y_train_test, y_val = train_test_split(X_data, y, random_state=42)

            #Get the cross val score
            scores = cross_val_score(clf, X_train_test, y_train_test)
            print(scores.mean())

            print("Printing prediction scores")

            clf = AdaBoostClassifier(algorithm="SAMME")
            clf.fit(X_train_test, y_train_test)
            print(sum(clf.predict(X_val) == y_val) / len(y_val))
            print("-------------")



def statistical_test(X, y):

    X, y = np.array(X), np.array(y)

    passed_idx = []

    for i in range(X.shape[1]):

        class_0 = [variable for variable, target in zip(X[:, i], y) if target == 0]
        class_1 = [variable for variable, target in zip(X[:, i], y) if target == 1]
        _, pnorm = mannwhitneyu(class_0, class_1)

        if pnorm <= 0.20:
            print(_, pnorm)
            print(i)
            passed_idx.append(i)
    
    #checking for cross cor
    removed_list = []        
    
    for indexes in list(itertools.combinations(passed_idx, 2)):
        results = pearsonr(X[:, indexes[0]], X[:, indexes[1]])

        if results.correlation > 0.9:
            print(f"Correlation between {indexes} is to high, discarding the second feature")
            removed_list.append(indexes[1])

    passed_idx = [idx for idx in passed_idx if idx not in removed_list]

    rus = RandomUnderSampler(random_state=42)
    X, y = rus.fit_resample(X, y)

        
    X_train_test, X_val, y_train_test, y_val = train_test_split(X, y, random_state=42)

    for indexes in list(itertools.chain(*[itertools.combinations(passed_idx, i) for i in range(1, len(passed_idx)+1)])):
        clf = LogisticRegression(max_iter=1000)

        print(indexes)

        try:
            clf.fit(X_train_test[:, indexes], y_train_test)
            print(sum(clf.predict(X_val[:, indexes]) == y_val) / len(y_val))

        except:
            print(f"Fitting the model with following indexes failed {indexes}, moving on...")
    


# train_and_predict(X, y, total_amount_features=20, use_combinations=False)

statistical_test(X, y)



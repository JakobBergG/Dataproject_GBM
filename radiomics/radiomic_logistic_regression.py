import csv
import json
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
import itertools
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from scipy.stats import mannwhitneyu, pearsonr


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



X = []
y = []

        
for patient, info in patient_info.items():
    X.append([value for _, value in info["features"].items()])
    y.append(info["TumorClass"])


def statistical_test(X, y):
    """
    Uses the same test as described in the paper. Makes the mannwhitney test for
    each feature and test for a p-value. For the given features we test for correlation
    and if a correlation surpasses a threshold, we discard one of the features. It 
    then tries to fit a combination of the features to the logistic regression.
    This should be made with a stepwise feature selection, but it is not.
    """

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


        try:
            clf.fit(X_train_test[:, indexes], y_train_test)
            y_pred = clf.predict(X_val[:, indexes])
            print(sum(y_pred == y_val) / len(y_val))

            if len(indexes) == 3:
                cm = confusion_matrix(y_val, y_pred, labels=clf.classes_)

                disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)

                # Plot the confusion matrix
                disp.plot(cmap=plt.cm.Blues)

                plt.title(f"Confusion Matrix for the logistic regression with {len(indexes)} features")
                plt.show()

                print(indexes)

        except:
            print(f"Fitting the model with following indexes failed {indexes}, moving on...")
    

statistical_test(X, y)

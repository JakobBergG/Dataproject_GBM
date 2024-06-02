import csv
import json
from sklearn.ensemble import AdaBoostClassifier
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
import pandas as pd

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

def train_and_predict(X, y, total_amount_features = 3):
    """
    Tries to train and predict the distanct and local tumors. Uses the ADABoost algorithm 
    to make the prediciton. Splits the data so we have equal number in each class, 
    and runs feature importance on k-folds. Uses the most important features on the 
    cross-validated plot and on the whole dataset, and makes plot for specific 
    number of features
    """

    X, y = np.array(X), np.array(y)
    #Splitting the data into equal sizes of classes
    rus = RandomUnderSampler(random_state=42)
    X, y = rus.fit_resample(X, y)

    clf = AdaBoostClassifier(algorithm="SAMME")

    kf  = KFold(n_splits=5)

    all_feature_importances = []

    accurary = []
    
    #splitting the features so we have some data to validate the features on
    X_train_test, X_val, y_train_test, y_val = train_test_split(X, y, random_state=42)

    for train_index, test_index in kf.split(X_train_test):

        # print(train_index, test_index)
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

    print("Mean Feature Importances:\n", mean_feature_importances)
    #get the mean of the accuracy
    accurary = np.mean(accurary)

    sorted_features = np.argsort(mean_feature_importances)[::-1]
    
    print("Top 3:", mean_feature_importances[sorted_features[:3]])

    # print(sorted_features)
    # print(accurary)

    for i in range(1, min(len(sorted_features), total_amount_features)):
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

        clf = AdaBoostClassifier(algorithm="SAMME", n_estimators=50, learning_rate=0.1)
        clf.fit(X_train_test, y_train_test)
        y_pred = clf.predict(X_val)
        print(sum(y_pred == y_val) / len(y_val))

        if i == 4:
            cm = confusion_matrix(y_val, y_pred, labels=clf.classes_)

            # Display the confusion matrix using ConfusionMatrixDisplay
            disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)

            # Plot the confusion matrix
            disp.plot(cmap=plt.cm.Blues)
            plt.show()

            print(top_indicies)

            feature_importances = clf.feature_importances_

            print("4 Feature Model Importances:", feature_importances)
            # Get the feature names
            feature_names = ['original_shape_Sphericity', 'original_glszm_GrayLevelNonUniformity', 'original_shape_SurfaceVolumeRatio', 'original_glcm_JointEntropy']

            # Create a DataFrame for better visualization
            feature_importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': feature_importances
            }).sort_values(by='Importance', ascending=False)

            # Plot the feature importances
            plt.figure(figsize=(10, 6))
            plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
            plt.xlabel('Feature Importance')
            plt.ylabel('Feature')
            plt.title('Feature Importance in AdaBoost Classifier')
            plt.gca().invert_yaxis()  # Invert y-axis to display the highest importance at the top
            plt.yticks(fontsize=5.5, rotation=45) 
            plt.show()

        print("-------------")

train_and_predict(X, y, total_amount_features=10)
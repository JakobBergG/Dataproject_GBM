import csv
import json
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import numpy as np

# Study_ID: 0, TumorLabel: 1, TumorClass: 2 
journal_path = "D:\\GBM\\radiomic_results\\overview.csv"
all_local_distant = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features.json"
all_combined = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_combined.json"
output_path = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_all_classes.json"

# Structure is {id, {features}}
# LOAD RADIOMIC FEATURES #
with open(all_local_distant, "r") as f:
    features_local_distant = json.load(f)
print("Local / distant:", len(features_local_distant.items()))

with open(all_combined, "r") as f:
    features_combined = json.load(f)
print("Combined:", len(features_combined.items()))

for id, features in features_combined.items():
    features_local_distant[id] = features
print("Total:", len(features_local_distant.items()))

# with open(output_path, "w") as f:
#     json.dump(features_local_distant, f)
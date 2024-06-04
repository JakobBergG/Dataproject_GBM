import json

"""
Script to quickly find the names of features
"""
all_radiomic_features_path = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_all_classes.json"

with open(all_radiomic_features_path) as f:
    all_radiomic_features = json.load(f)

features = [feature for feature, value in all_radiomic_features["3017"].items()]

indices = (65, 66, 76)

print([features[i] for i in indices])
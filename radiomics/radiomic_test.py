import json

all_radiomic_features_path = "D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_all_features_all_classes.json"

with open(all_radiomic_features_path) as f:
    all_radiomic_features = json.load(f)

print(len(all_radiomic_features.items()))
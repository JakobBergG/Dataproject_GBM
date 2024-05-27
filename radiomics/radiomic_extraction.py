import os
from radiomics import featureextractor
from sklearn.linear_model import LogisticRegression
import json
import csv
"""
Script to extract radiomic features from MR scans using the CTV ring.
Uses:
- List of avaiable patients to extract features from.
- List of what hospital the patients belong to, to know which hospital folder to retrieve images from.
- Filepath to folder containing MR image
- Filepath to folder containing the CTV ring. (Region of interest)
- Output filepath
"""

# READ AVAILABLE PATIENTS #
with open("D:\\GBM\\radiomic_results\\available_patients_time2_combined.json", "r") as f:
    available_patients = json.load(f)

# FIND HOSPITAL OF PATIENTS #
# To know where to look for the patient's images
patient_location = {}
with open("D:\\GBM\\radiomic_results\\overview_with_combined.csv", "r", encoding="utf-8-sig") as f:
    rows = csv.reader(f, delimiter=",")
    names = next(rows) # The first row gives the names of the columns
    
    # Now read info for all patients
    for row in rows:
        location = row[0]
        study_id = f"{row[1]:>04}" # Pad with 4 zeros
        patient_location[study_id] = location

# INITIALIZE THE FEATURE EXTRACTOR #
extractor = featureextractor.RadiomicsFeatureExtractor("radiomics\Params.yaml")

def extract_features(image_path, mask_path):
    """Extract and return radiomic features
    """
    result = extractor.execute(image_path, mask_path)

    # Grab useful metrics
    features = {}
    for key, value in result.items():
        if not key.startswith("diagnostics"): # Do not include diagnostic info - See also radiomics/Params.yaml for extracted features
            features[key] = float(value) # Value is originally ndarray - can't be serialized to json
    
    return features

# RUN EXTRACTION FOR PATIENTS #
number_of_patients = len(available_patients)
progress_counter = 0

all_patient_features = {}
for patient_id in available_patients: 
    mask_path = f"D:\\GBM\\radiomic_results\\masks\\time2\\GTV_rings_combined\\{patient_id}\\{patient_id}_mask_ring.nii.gz"

    image_path = f"D:\\GBM\\uni_gtv_tr_data\\{patient_location[patient_id]}\\{patient_id}\\{patient_id}_stripped.nii.gz"

    progress_counter += 1
    print("Calculating features for id:", patient_id, f"| {progress_counter} / {number_of_patients} ({progress_counter / number_of_patients * 100:.0f}%)")
    try:
        all_patient_features[patient_id] = extract_features(image_path, mask_path)
    except Exception as e:
        print("Error happened while extracting features, skipping patient!\n", e)
        with open("D:\\GBM\\radiomic_results\\error_logging.txt", 'a') as f:
            f.write("*" * 10 + f"\nError happened with patient: 2\n" + str(e) + "\n" + "*" * 10 + "\n")

# PRINTING - OPTIONAL #
do_print = False
if do_print:
    for patient_no, features in all_patient_features.items():
        print("-" * 10, "PATIENT:", patient_no, "-" * 10)
        for key,value in features.items():
            print((key + " ").ljust(50, "-"), ":", value)
        print("")

# SAVE #
with open("D:\\GBM\\radiomic_results\\feature_output\\time2\\patients_test.json", "w") as f:
    json.dump(all_patient_features, f)
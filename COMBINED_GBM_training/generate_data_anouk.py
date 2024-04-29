import os
import re
import shutil



# training_images_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\\imagesTr"
# training_labels_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\labelsTr"
# test_images_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\\imagesTs"
# test_labels_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\\labelsTs"

# training_images = [f.path for f in os.scandir(training_images_path)]
# for image in training_images:
#     new_name = re.sub("GBM_", "", image)
#     new_name = re.sub("_0000", "_stripped", new_name)
#     os.rename(image, new_name)


# test_images = [f.path for f in os.scandir(test_images_path)]
# for image in test_images:
#     new_name = re.sub("GBM_", "", image)
#     new_name = re.sub("_0000", "_stripped", new_name)
#     os.rename(image, new_name)


# training_labels = [f.path for f in os.scandir(training_labels_path)]
# for label in training_labels:
#     new_name = re.sub("GBM_", "", label)
#     new_name = re.sub(".nii.gz", "_gtv.nii.gz", new_name)
#     os.rename(label, new_name)

# test_labels = [f.path for f in os.scandir(test_labels_path)]
# for label in test_labels:
#     new_name = re.sub("GBM_", "", label)
#     new_name = re.sub(".nii.gz", "_gtv.nii.gz", new_name)
#     os.rename(label, new_name)


def get_number(n):
    if n < 10:
        return "000" + str(n)
    if n < 100:
        return "00" + str(n)
    if n < 1000:
        return "0" + str(n)
    if n < 10000:
        return str(n)


# images_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\\"
# labels_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK\\"

# images = [f.path for f in os.scandir(images_path)]
# labels = [f.path for f in os.scandir(labels_path)]

# for image in images:
#     patient_number = re.findall(r'\d+', os.path.basename(image))[0]
#     patient_number = get_number(int(patient_number))
#     hospital_folder_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK"
#     patient_folder_path = os.path.join(hospital_folder_path, patient_number)
#     if not os.path.exists(patient_folder_path):
#         os.mkdir(patient_folder_path)
#     dest = patient_folder_path
#     shutil.move(image,dest)

# for label in labels:
#     patient_number = re.findall(r'\d+', os.path.basename(label))[0]
#     patient_number = get_number(int(patient_number))
#     hospital_folder_path = "D:\\GBM\\uni_gtv_tr_data\\ANOUK"
#     patient_folder_path = os.path.join(hospital_folder_path, patient_number)
#     if not os.path.exists(patient_folder_path):
#         os.mkdir(patient_folder_path)
#     dest = patient_folder_path
#     shutil.move(label,  dest)

patients = [f.path for f in os.scandir("D:\\GBM\\uni_gtv_tr_data\\ANOUK")]

for patient in patients:
    patient_number = os.path.basename(patient)
    new_name_label = f"{patient_number}_gtv.nii.gz"
    new_name_image = f"{patient_number}_stripped.nii.gz"
    label = [f.path for f in os.scandir(patient) if f.path.endswith("gtv.nii.gz")][0]
    image = [f.path for f in os.scandir(patient) if f.path.endswith("stripped.nii.gz")][0]
    os.rename(label, f"{patient}\\{new_name_label}")
    os.rename(image, f"{patient}\\{new_name_image}")

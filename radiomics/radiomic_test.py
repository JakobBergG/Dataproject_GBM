import os

datapath = "D:\\GBM\\summary\\AUH"

patient_numbers = os.listdir(datapath)

patient_folder = os.listdir(os.path.join(datapath, patient_numbers[0]))

for file_name in os.listdir(os.path.join(datapath, "0114")):
    print(file_name)
    if file_name.startswith("time0") and file_name.endswith("gtv.nii.gz"):
        label_path = file_name
    elif file_name.startswith("time0") and file_name.endswith("MR.nii.gz"):
        image_path = file_name
    
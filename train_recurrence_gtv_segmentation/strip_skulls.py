import os
import SimpleITK as sitk
import re


# MODIFIED VERSION OF run_skull_stripping
def run_skull_stripping(patient_folder):
    print(f"running on folder {os.path.basename(patient_folder)}")
    '''
    Skullstrip all MR scans for patient
    '''
    # find all mr scans
    try:
        patient_filelist = [f.path for f in os.scandir(patient_folder)]
        mr_list = []
        ct_list = []
        for file in patient_filelist:
            if os.path.basename(file).endswith("_MR.nii.gz"): # Used to be "_MR_res.nii.gz"
                mr_list.append(file)
            if os.path.basename(file).endswith("_CT.nii.gz"): # Used to be "_MR_res.nii.gz"
                ct_list.append(file)

        # find mask:
        mask_path = None
        new_mask_path = os.path.join(patient_folder, "brain_mr", "output_brains")
        mask_filelist = [f.path for f in os.scandir(new_mask_path)]
        for file in mask_filelist:
            if os.path.basename(file).endswith("mask.nii.gz"):
                mask_path = os.path.join(new_mask_path, os.path.basename(file))

        if not mask_path:
            print(f"could not find mask_path for patient {os.path.basename(patient_folder)}")
            return
        
        # now strip mr skulls
        for mr in mr_list:
            mr_name = os.path.basename(mr)
            output_name = re.sub("_MR", "_MR_stripped", mr_name)
            output_path = os.path.join(patient_folder, output_name)
            scan = sitk.ReadImage(mr)
            mask = sitk.ReadImage(mask_path)
            stripped_skull = sitk.Mask(scan, mask) 
            sitk.WriteImage(stripped_skull, output_path)
    except Exception as e:
        print(f"error for patient {patient_folder}: {e}")

path_data = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"
patient_folders = [f.path for f in os.scandir(path_data) if f.is_dir()]

for patient_folder in patient_folders:
    run_skull_stripping(patient_folder)


"""
import os
import SimpleITK as sitk
import re


# MODIFIED VERSION OF run_skull_stripping
def run_skull_stripping(patient_folder):
    print(f"running on folder {os.path.basename(patient_folder)}")
    '''
    Skullstrip all MR scans for patient
    '''
    # find all mr scans
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    mr_list = []
    ct_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith("_MR.nii.gz"): # Used to be "_MR_res.nii.gz"
            mr_list.append(file)
        if os.path.basename(file).endswith("_CT.nii.gz"): # Used to be "_MR_res.nii.gz"
            ct_list.append(file)

    # find mask:
    mask_path = None
    for file in patient_filelist:
        if os.path.basename(file).endswith("Brain.nii.gz"):
            mask_path = os.path.join(patient_folder, os.path.basename(file))
    if not mask_path:
        print(f"could not find mask_path for patient {os.path.basename(patient_folder)}")
        return
    # now strip mr skulls
    for mr in mr_list:
        mr_name = os.path.basename(mr)
        output_name = re.sub("_MR", "_MR_stripped", mr_name)
        output_path = os.path.join(patient_folder, output_name)
        scan = sitk.ReadImage(mr)
        mask = sitk.ReadImage(mask_path)
        stripped_skull = sitk.Mask(scan, mask) 
        sitk.WriteImage(stripped_skull, output_path)

path_data = "C:\\Users\\Student1\\Desktop\\stripped_recurrence"
patient_folders = [f.path for f in os.scandir(path_data) if f.is_dir()]

for patient_folder in patient_folders:
    run_skull_stripping(patient_folder)

"""

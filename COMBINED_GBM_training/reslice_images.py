# This file will reslice the images in the uni_GTV_tr_data folder such that for each patient
# the stripped MR scan has the same voxel spacing as the gtv (label) file.
import os
import SimpleITK as sitk
import re

def reslice_image(itk_image : sitk.Image, itk_ref : sitk.Image , is_label : bool = False) -> sitk.Image:
    '''Reslice one image to the grid of another image (when they are registered)'''
    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(itk_ref)
    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)

hospitals = ["AUH", "OUH", "CUH", "RECURRENCE", "ANOUK"]

for hospital in hospitals:
    hospital_data_path = os.path.join("D:\\GBM\\uni_gtv_tr_data", hospital)
    patient_files = [f.path for f in os.scandir(hospital_data_path)]
    for patient_file in patient_files:
        # get the stripped MR scan and label
        scans = [f.path for f in os.scandir(patient_file)]
        try:
            stripped_MR_name = [scan for scan in scans if scan.endswith("stripped.nii.gz")][0]
            gtv_name = [scan for scan in scans if scan.endswith("gtv.nii.gz")][0]
        except Exception as e:
            print(f"could not get scans for patient {os.path.basename(patient_file)}: {e}")
        stripped_MR = sitk.ReadImage(stripped_MR_name)
        gtv = sitk.ReadImage(gtv_name)
        resliced_stripped_MR = reslice_image(stripped_MR, gtv, is_label=True)
        print(stripped_MR_name)
        resliced_MR_name = re.sub(".nii.gz", "_resliced.nii.gz", stripped_MR_name)
        sitk.WriteImage(resliced_stripped_MR, resliced_MR_name)



import SimpleITK as sitk
import os

basepath_ct = "E:/Jasper/nnUNet/nnUNet_raw_data/Task800_GBM_CT/labelsTr"
basepath_mr = "E:/Jasper/nnUNet/nnUNet_raw_data/Task801_GBM/labelsTr"

ct_files = [f.path for f in os.scandir(basepath_ct)]
mr_files = [f.path for f in os.scandir(basepath_mr)]

ct_scans_with_small_objects = 0
mr_scans_with_small_objects = 0

def n_small_objects(label_file : str) -> bool:
    '''Returns true if the scan has small objects
    '''
    label_image = sitk.ReadImage(label_file)
    connected_component = sitk.ConnectedComponentImageFilter()
    connected_component.Execute(label_image)
    return connected_component.GetObjectCount()

for label_image in ct_files:
    n = n_small_objects(label_image)
    if n >= 2:
        print(f"{n} små objekter (CT) i {label_image}")
        ct_scans_with_small_objects +=1

for label_image in mr_files:
    n = n_small_objects(label_image)
    if n >= 2:
        print(f"{n} små objekter (MR) i {label_image}")
        mr_scans_with_small_objects +=1




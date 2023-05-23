import SimpleITK as sitk
import os

basepath_ct = "E:/Jasper/nnUNet/nnUNet_raw_data/Task800_GBM_CT/labelsTr"
basepath_mr = "E:/Jasper/nnUNet/nnUNet_raw_data/Task801_GBM/labelsTr"

ct_files = [f.path for f in os.scandir(basepath_ct)]
mr_files = [f.path for f in os.scandir(basepath_mr)]

ct_scans_with_small_objects = 0
mr_scans_with_small_objects = 0

def size_second_largest(label_file : str, ignore_threshold = 5) -> bool:
    '''Returns volume of second largest tumor is above threshold
    '''
    label_image = sitk.ReadImage(label_file)
    connected_component = sitk.ConnectedComponentImageFilter()
    connected_component.Execute(label_image)
    n = connected_component.GetObjectCount()
    if n >= 2:
        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.Execute(label_image)
        component_sizes = sorted([stats.GetNumberOfPixels(l) for l in stats.GetLabels()], reverse=True)
        if component_sizes[1] > ignore_threshold: # er den andenstørste for stor?
            return component_sizes[1]
        
    return -1

for label_image in ct_files:
    vol = size_second_largest(label_image)
    if vol != -1:
        print(f"Big ({vol} voxels) second largest component in {label_image}")
        ct_scans_with_small_objects +=1

for label_image in mr_files:
    vol = size_second_largest(label_image)
    if vol != -1:
        print(f"Big ({vol} voxels) second largest component in {label_image}")
        mr_scans_with_small_objects +=1


print(f"{ct_scans_with_small_objects =}")
print(f"{mr_scans_with_small_objects =}")



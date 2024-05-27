import SimpleITK as sitk
import os
import json
"""
Script to create the CTV ring
To create CTV ring it needs:
- GTV
- MR scan
- Brainmask
"""


def filter_mask(mask_path, brain_mask_path, output_path, use_largest_lesion=False):
    """Create and write CTV ring to disk.

    
    Keyword arguments:
    mask_path -- the filepath to the GTV mask
    brain_mask_path -- the filepath to the brain mask
    output_path -- filepath of the output image
    use_largest_lesion -- filter so only the largest lesion is included in the CTV ring
    """

    gtv_mask = sitk.ReadImage(mask_path)
    if use_largest_lesion:
        gtv_mask = get_largest_lesion(gtv_mask)

    # DILATION - In paper: 2 cm
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelType(sitk.sitkBall)
    radius = 20 # in mm. DICOM standard
    dilate_filter.SetKernelRadius((radius, radius, radius // 2)) # For an input image voxel spacing of 1, 1, 0.5.
    dilate_filter.SetForegroundValue(1)

    new_mask = dilate_filter.Execute(gtv_mask)

    # SKULL AS DILATION BOUNDARY - Make sure the dilation doesn't cross the skull
    and_filter = sitk.AndImageFilter()
    brain_mask = sitk.ReadImage(brain_mask_path)

    new_mask = and_filter.Execute(new_mask, brain_mask)

    # REMOVE GTV AREA - We seek to extract features from the RING around the GTV.
    subtract_filter = sitk.SubtractImageFilter()

    new_mask = subtract_filter.Execute(new_mask, gtv_mask)

    # SAVE NEW MASK
    sitk.WriteImage(new_mask, output_path)

def get_largest_lesion(mask, verbose = False):
    '''Return the largest lesion (tumor).

    Verbose also prints the size of the largest lesion
    '''
    component_image = sitk.ConnectedComponent(mask)
    sorted_component_image = sitk.RelabelComponent(component_image, sortByObjectSize=True)
    largest_component_binary_image = sorted_component_image == 1

    if verbose:
        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.Execute(largest_component_binary_image)
        print("Found largest lesion with size:", stats.GetNumberOfPixels(1))

    return largest_component_binary_image


with open("D:\\GBM\\radiomic_results\\available_patients_time2_combined.json", "r") as f:
    available_patients = json.load(f)

number_of_patients = len(available_patients)
progress_counter = 0
 
for hospital in ["AUH", "OUH", "CUH"]:
    patients = os.listdir(f"D:\\GBM\\uni_gtv_tr_data\\{hospital}")

    for patient_id in patients:
        if patient_id not in available_patients:
            continue
        output_path = f"D:\\GBM\\radiomic_results\\masks\\time2\\GTV_rings_combined\\{patient_id}"

        # Create directory for patient
        progress_counter += 1
        print("Now running for id:", patient_id, f"| {progress_counter} / {number_of_patients} ({progress_counter / number_of_patients * 100:.0f}%)")
        try:
            os.mkdir(output_path)
        except OSError:
            print("Folder already existed", patient_id)

        # Define paths to masks
        mask_path = f"D:\\GBM\\radiomic_results\\masks\\time2\\GTV_resampled\\{patient_id}_mask.nii.gz"
        brain_mask_path = f"D:\\GBM\\uni_gtv_tr_data\\{hospital}\\{patient_id}\\{patient_id}_mask.nii.gz"
        output_filepath = output_path + f"\\{patient_id}_mask_ring.nii.gz"

        try:
            filter_mask(mask_path, brain_mask_path, output_filepath)
        except Exception as e:
            print("Error happened:\n", e, "\nRemoving created directory.")
            os.rmdir(output_path)

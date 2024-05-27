import SimpleITK as sitk
import numpy as np
import os
"""
The clinical delineation of the GTV has different dimensions and voxel spacings than the MR scan and brain mask.
This is because the MR and brain mask has been throuhgh the pipeline that automatically resamples the images to a common spacing, 
while the clinical delineations have different spacings depending on the location from where it was delineated.
"""

def resample_image(itk_image, out_spacing=[1, 1, 1.0], is_label=False, refer_img = None):
    """Return an image with resampled voxel spacing
    
    Keyword arguments:
    out_spacing -- the desired spacing of the output image
    is_label -- whether or not the image is a label (i.e. image has only 0 or 1 as voxel intensities)
    refer_img -- option to have output image have same origin as a reference image.
    """
    
    original_spacing = itk_image.GetSpacing()
    original_size = itk_image.GetSize()

    out_size = [
        int(np.round(original_size[0] * (original_spacing[0] / out_spacing[0]))),
        int(np.round(original_size[1] * (original_spacing[1] / out_spacing[1]))),
        int(np.round(original_size[2] * (original_spacing[2] / out_spacing[2])))
    ]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(out_spacing)
    resample.SetSize(out_size)
    resample.SetOutputDirection(itk_image.GetDirection())


    if refer_img != None:
        resample.SetOutputOrigin(refer_img.GetOrigin())
    else:
        resample.SetOutputOrigin(itk_image.GetOrigin())

    resample.SetTransform(sitk.Transform())
    default_value = np.float64(sitk.GetArrayViewFromImage(itk_image).min())
    resample.SetDefaultPixelValue(default_value)# itk_image.GetPixelIDValue())

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline) # sitkLinear)#

    return resample.Execute(itk_image)

### Resample GTV scans from uni_gtv_tr_data

for hospital in ["AUH", "CUH", "OUH"]:
    for patient_id in os.listdir(f"D:\\GBM\\uni_gtv_tr_data\\{hospital}"):
        print("Patient", patient_id, "-", hospital)
        gtv_path = f"D:\\GBM\\uni_gtv_tr_data\\{hospital}\\{patient_id}\\{patient_id}_gtv.nii.gz"
        gtv_mask = sitk.ReadImage(gtv_path)

        new_mask = resample_image(gtv_mask, is_label=True)

        output_path = f"D:\\GBM\\radiomic_results\\resampled_GTVs\\time2\\{patient_id}_mask.nii.gz"
        sitk.WriteImage(new_mask, output_path)
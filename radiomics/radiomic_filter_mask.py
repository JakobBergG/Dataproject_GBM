import SimpleITK as sitk

def filter_mask(mask_path, brain_mask_path, output_path):
    gtv_mask = sitk.ReadImage(mask_path)

    # DILATION - In paper: 2 cm
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelType(sitk.sitkBall)
    radius = 20 # in mm. DICOM standard
    dilate_filter.SetKernelRadius((radius, radius, radius // 2)) # Due to OUR sampling of images 1, 1, .5
    dilate_filter.SetForegroundValue(1)

    new_mask = dilate_filter.Execute(gtv_mask)

    # SKULL AS DILATION BOUNDARY - Make sure the dilation doesn't cross the skull
    and_filter = sitk.AndImageFilter()
    brain_mask = sitk.ReadImage(brain_mask_path)
    new_mask = and_filter.Execute(new_mask, brain_mask)

    # REMOVE GTV AREA - We seek to extract features from the ring around the GTV.
    subtract_filter = sitk.SubtractImageFilter()

    new_mask = subtract_filter.Execute(new_mask, gtv_mask)

    # SAVE NEW MASK
    sitk.WriteImage(new_mask, output_path)

mask_path = "D:\\GBM\output\\AUH\\0114\\predicted_gtvs\\0114_20140723_gtv.nii"
brain_mask_path = "D:\\GBM\\output\\AUH\\0114\\brain_mr\\output_brains\\0114_20140723_MR_mask_cleaned.nii"
output_path = "D:\\GBM\\output_test\\radiomic_results\\test.nii.gz"

filter_mask(mask_path, brain_mask_path, output_path)
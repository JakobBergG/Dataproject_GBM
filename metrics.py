import SimpleITK as sitk
import numpy as np


# count the number of voxels in a mask
def volume_mask(image : sitk.Image) -> int:
    im_view = sitk.GetArrayViewFromImage(image)
    return np.count_nonzero(im_view)


# return volume of mask in cubic centimetres
def volume_mask_cc(image : sitk.Image) -> float:
    spacing = image.GetSpacing()
    return spacing[0] * spacing[1] * spacing[2] * volume_mask(image) / 1000.0
    

# return percentage of overlap between gtv and (95%) dose
def mask_overlap(gtv : sitk.Image, dose : sitk.Image) -> float:
    return volume_mask(dose*gtv) / volume_mask(gtv)


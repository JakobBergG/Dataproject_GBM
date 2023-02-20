import SimpleITK as sitk
import numpy as np


# count the number of voxels in a mask
def volume_mask(image : sitk.Image) -> int:
    im_view = sitk.GetArrayViewFromImage(image)
    return np.count_nonzero(im_view)

# return volume of mask in cubic centimetres
def volume_mask_cc(image : sitk.Image) -> int:
    spacing = image.GetSpacing()
    return spacing[0] * spacing[1] * spacing[2] * volume_mask(image) / 1000.0

import SimpleITK as sitk
import numpy as np


def volume_mask(image : sitk.Image) -> int:
    '''Count the number of voxels in a mask'''
    im_view = sitk.GetArrayViewFromImage(image)
    return np.count_nonzero(im_view)


def volume_mask_cc(image : sitk.Image) -> float:
    '''Get volume of mask in cubic centimetres'''
    spacing = image.GetSpacing()
    return spacing[0] * spacing[1] * spacing[2] * volume_mask(image) / 1000.0
    

def mask_overlap(gtv : sitk.Image, dose : sitk.Image) -> float:
    '''Get percentage of overlap between gtv and (95%) dose'''
    return volume_mask(dose*gtv) / volume_mask(gtv)


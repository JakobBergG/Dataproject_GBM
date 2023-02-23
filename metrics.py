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


def dose_percentage_region(dose_image : sitk.Image, target_intensity : float, percentage : float = 0.95) -> float:
    '''Create a mask of where the dose is above a certain percentage of the
      target intensity (e.g. 95% of 60 Gy)'''
    return dose_image > target_intensity * percentage

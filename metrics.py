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


def volume_component_cc(image : sitk.Image) -> float:
    '''Get volume pr. lession from component image in cubic centimetres'''
    spacing = image.GetSpacing()
    
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(image)
    component_sizes = [spacing[0] * spacing[1] * spacing[2] * stats.GetNumberOfPixels(l) /1000 for l in stats.GetLabels()]
    return component_sizes

def mask_overlap(gtv : sitk.Image, dose : sitk.Image) -> float:
    '''Get percentage of overlap between gtv and (95%) dose'''
    return volume_mask(dose*gtv) / volume_mask(gtv)


def dose_percentage_region(dose_image : sitk.Image, target_intensity : float, percentage : float = 0.95) -> float:
    '''Create a mask of where the dose is above a certain percentage of the
      target intensity (e.g. 95% of 60 Gy)'''
    return dose_image > target_intensity * percentage


def get_target_dose (image: sitk.Image) -> int:
    '''Guess target dose from maximum value in dose image (54 or 60)'''
    MinMax = sitk.MinimumMaximumImageFilter()
    MinMax.Execute(image)
    if MinMax.GetMaximum()>60:
        return 60
    else:
        return 54
    

def label_image_connected_components(gtv_image : sitk.Image, minimum_lesion_size : int = 0):
    '''Create label image by calculating connected components from GTV.
    If minimum_lesion_size is specified, will remove any lesions with fewer voxels
    than minimum_lesion_size.
    Returns tuple (label_image, n_normal_lesions, n_tiny_lesions),
    where n_normal_lesions is the number of lesions with a size greater than
    minimum_lesion_size, and n_tiny lesions is the number of lesions with a size
    smaller than minimum_lesions_size.
    '''
    # get connected components
    connected_component = sitk.ConnectedComponentImageFilter()
    component_image = connected_component.Execute(gtv_image)
    n_lesions_complete = connected_component.GetObjectCount()

    # remove lesions that are too small
    label_component = sitk.RelabelComponentImageFilter()
    label_component.SetMinimumObjectSize(minimum_lesion_size)
    label_component.SetSortByObjectSize(True)
    label_image = label_component.Execute(component_image)

    n_normal_lesions = label_component.GetNumberOfObjects()
    n_tiny_lesions = n_lesions_complete - n_normal_lesions
    
    return  label_image, n_normal_lesions, n_tiny_lesions

import numpy as np
import medpy.metric
import SimpleITK as sitk
import common.utils as utils


def volume_mask(image : sitk.Image) -> int:
    '''Count the number of voxels in a mask'''
    im_view = sitk.GetArrayViewFromImage(image)
    return np.count_nonzero(im_view)


def volume_mask_cc(image : sitk.Image) -> float:
    '''Get volume of mask in cubic centimetres'''
    spacing = image.GetSpacing()
    return spacing[0] * spacing[1] * spacing[2] * volume_mask(image) / 1000.0


def volume_component_cc(image : sitk.Image) -> list:
    '''Get volume pr. lession from component image in cubic centimetres'''
    spacing = image.GetSpacing()
    
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(image)
    component_sizes = [spacing[0] * spacing[1] * spacing[2] * stats.GetNumberOfPixels(l) / 1000 for l in stats.GetLabels()]
    return component_sizes


def mask_overlap(image1 : sitk.Image, image2 : sitk.Image) -> float:
    '''Get percentage of overlap between gtv and (95%) dose'''
    vol1 = volume_mask(image1)
    if vol1>0:
        return volume_mask(image2*image1) / vol1
    else:
        raise Exception("Volune of mask is 0")


def dose_percentage_region(dose_image : sitk.Image, target_intensity : float, percentage : float = 0.95) -> float:
    '''Create a mask of where the dose is above a certain percentage of the
      target intensity (e.g. 95% of 60 Gy)'''
    return dose_image >= target_intensity * percentage


def get_target_dose (image: sitk.Image) -> int:
    '''Guess target dose from maximum value in dose image (54 or 60)'''
    MinMax = sitk.MinimumMaximumImageFilter()
    MinMax.Execute(image)
    if MinMax.GetMaximum() > 60:
        return 60
    else:
        return 54
    

def label_image_connected_components(gtv_image : sitk.Image, minimum_lesion_size : int = 0) -> tuple:
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


def type_recurrence(label_image : sitk.Image, baseline : sitk.Image) -> int:
    '''Get type of recurrence by using the visual scoring method.
    Type1: Local recurrence. (Overlap between baseline and recurrence GTV)
    Type3: Distant recurrence. (No overlap)
    Type2: Both local and distant recurrence
    '''
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(label_image)
    labels = stats.GetLabels()
    tumors = [label_image == l for l in labels]
    local = 0
    distant = 0
    for t in tumors:
        if mask_overlap(t, baseline)>0:
            local += 1
        else:
            distant += 1
    if distant > 0 and local > 0:
        return 2
    elif distant > 0:
        return 3
    elif local > 0:
        return 1


def classical_type_recurrence(percentage):
    '''Classical type of recurrence:
        Central: >95% of recurrence gtv within 95% isodose area
        In-field: 80%-95% of recurrence gtv within 95% isodose area    
        Marginal: 20%-80% of recurrence gtv within 95% isodose area
        Distant: <20% of recurrence gtv within 95% isodose area
        '''
    if percentage > 0.95:
        return "Central"
    elif percentage > 0.8:
        return "In-field"
    elif percentage > 0.2:
        return "Marginal"
    else: 
        return "Distant"


def get_hd(baseline : sitk.Image,rec : sitk.Image) -> tuple:
    '''Get hausdorff distance between tumor area at baseline and tumor area at recurrence
    Returns tuple (hd, hd95)'''
    rec = utils.reslice_image(rec, baseline, is_label=True)
    baseline_array = sitk.GetArrayFromImage(baseline)
    rec_array = sitk.GetArrayFromImage(rec)
    hd = medpy.metric.binary.hd(baseline_array, rec_array)
    hd95 = medpy.metric.binary.hd95(baseline_array ,rec_array )
    
    return hd, hd95


def msd(ct_mask : sitk.Image, mr_mask : sitk.Image) -> float:
    '''Calculate Mean Surface Distance between mr and ct brain masks.
    Returns float MSD(ct_mask, mr_mask)'''
    spacing = ct_mask.GetSpacing()
    mr_mask = utils.reslice_image(mr_mask, ct_mask, is_label=True)
    mr_mask_array = sitk.GetArrayFromImage(mr_mask)
    ct_mask_array = sitk.GetArrayFromImage(ct_mask)
    mean_surface_distance = medpy.metric.binary.assd(mr_mask_array, ct_mask_array, voxelspacing=spacing)
    
    return mean_surface_distance





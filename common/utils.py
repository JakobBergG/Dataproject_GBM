import SimpleITK as sitk
import os
import json
from datetime import datetime
import re
import logging

log = logging.getLogger(__name__)

# default settings
settings = {
    "task_id_brain_segmentation_ct": 800,
    "task_id_brain_segmentation_mr": 801,
    "skull_stripping_dilation_radius_ct": [2, 2, 2], # expand 2 mm in all directions
    "skull_stripping_dilation_radius_mr": [4, 4, 2], # also expand 2 mm : remember spacing is 0.5x0.5x1.0
    "registration_dilation_radius_mr": [5, 5, 5],
    "registration_dilation_radius_ct": [10, 10, 5]
}

# load settings file, change default settings
if not os.path.isfile("settings.json"):
    log.warning("No settings.json, using default settings")
else:
    with open("settings.json", "r") as f:
        new_settings : dict = json.load(f)
        for key, value in new_settings.items():
            settings[key] = value

# log settings
for key, value in settings:
    log.info("Setting {key} = {value}")


def get_path(location_name : str) -> str:
    '''Given location_name (e.g. data, output), returns path given in settings.json
    If no settings.json, use defaut values'''
    default_paths = {
        "path_data": "data/",
        "path_info": "info/",
        "path_output": "output/",
        "local_path_gtv": "predicted_gtvs",
        "local_path_brain_mr": "brain_mr",
        "local_path_brain_ct": "brain_ct",
        "local_path_brainmasks_mr": "brain_mr/output_brains",
        "local_path_brainmasks_ct": "brain_ct/output_brains",
        "local_path_moved_mr": "MR_to_CT_mask",
        "local_path_moved_gtv": "MR_to_CT_gtv"
    }
    assert location_name in default_paths, f"Location name {location_name} not valid"

    # if path exists in settings, return path given there. Else, return default path
    return settings.get(location_name, default_paths[location_name])


def get_setting(setting_name : str):
    assert setting_name in settings, f"Setting {setting_name} not in settings"
    return settings[setting_name]


def reslice_image(itk_image : sitk.Image, itk_ref : sitk.Image , is_label : bool = False) -> sitk.Image:
    '''Reslice one image to the grid of another image (when they are registered)'''
    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(itk_ref)

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)


def parse_filename(filename : str) -> tuple:
    '''Given a filename, extracts the tuple (patient_id, date, scantype, datatype)'''
    parts = re.split("[_.]", filename) # split at either _ or .
    patient_id, datestring, scantype, datatype = parts[:4]
    patient_id = int(patient_id)

    date = datetime.strptime(datestring, "%Y%m%d")
    return patient_id, date, scantype, datatype


def date_to_relative_time(date : datetime, base_date : datetime) -> float:
    '''Returns date with relative time in days relative to base date'''
    return (date - base_date).total_seconds() / 86400

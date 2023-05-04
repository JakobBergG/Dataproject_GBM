import SimpleITK as sitk
import os
import json
from datetime import datetime
import re
import logging

log = logging.getLogger(__name__)

# default settings
settings = {
    # nnUNet model task ids
    "task_id_brain_segmentation_ct": 800,
    "task_id_brain_segmentation_mr": 801,
    "task_id_gtv_segmentation": 600,
    # dilation radii
    "skull_stripping_dilation_radius_mr": [4, 4, 2], # expand 2 mm : remember spacing is 0.5x0.5x1.0
    "registration_dilation_radius_mr": [10, 10, 5],
    "registration_dilation_radius_ct": [5, 5, 5],
    # paths
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

# load settings file, change default settings
if not os.path.isfile("settings.json"):
    log.warning("No settings.json, using default settings")
else:
    with open("settings.json", "r") as f:
        new_settings : dict = json.load(f)
        for key, value in new_settings.items():
            settings[key] = value

# log settings
for key, value in settings.items():
    log.info(f"Setting {key} = {value}")


def get_path(location_name : str) -> str:
    '''Given location_name (e.g. data, output), returns path given in settings'''
    assert location_name in settings, f"Location name {location_name} not valid"
    return settings[location_name]


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


def test_symbolic_link_permission():
    '''This function raises an exception if the system is not allowed to create
    symbolic links. On windows, you must run in administrator mode'''
    with open("_symlink_test", "w") as f:
        f.write("test")
    try:
        os.symlink("_symlink_test", "_symlink_test_link")
        os.remove("_symlink_test")
        os.remove("_symlink_test_link")
    except:
        raise Exception("Not allowed to create symbolic links. If on Windows, run in adminstrator mode")
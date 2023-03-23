import SimpleITK as sitk
import os
import json
from datetime import datetime
import re
import csv


def get_path(location_name : str) -> str:
    '''Given location_name (e.g. data, output), returns path given in settings.json
    If no settings.json, use defaut values'''
    default_paths = {
        "path_data": "data/",
        "path_info": "info/",
        "path_output": "output/",
        "local_path_gtv": "MR_TO_CT",
        "local_path_brain_mr": "nnunet_brain_mr",
        "local_path_brain_ct": "nnunet_brain_ct"
    }
    assert location_name in default_paths, f"Location name {location_name} not valid"

    if not os.path.isfile("settings.json"):
        print("Warning: No settings.json, using default settings")
        return default_paths[location_name]

    with open("settings.json", "r") as f:
        settings : dict = json.load(f)
    
    # if path exists in settings, return path given there. Else, return default path
    return settings.get(location_name, default_paths[location_name])


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


def load_journal_info_patients(path : str) -> dict:
    '''Loads .csv file with info about patient. Returns dictionary
    with key for each patient'''

    # these following columns should be read, and the following functions should be called
    to_read = {
        "Study_ID": str,
        "MRIDiagDate_checked": str,
        "MRIPostopDate_checked": str,
        "RT_MRIDate": str,
        "ProgressionDate": str,
        "RTdoseplan": lambda x : int(float(re.sub(",", ".", x))),
        "Age_at_diagn": lambda x : float(re.sub(",", ".", x)),
        "Sex" : str,
        "ProgressionType": int
    }

    # create dict to hold all patients
    journal_info_patients = {}

    with open(path, newline='', mode="r", encoding="utf-8-sig") as f:
        rows = csv.reader(f, delimiter=";")
        names = next(rows) # the first row gives the names of the columns
        
        # now read info for all patients
        for row in rows:
            # create dict for each patient
            patient_dict = {}
            for i, name in enumerate(names):
                if name == "Study_ID":
                    study_id = f"{row[i]:>04}" #pad with 4 zeros
                elif name in to_read:
                    func = to_read[name]
                    patient_dict[name] = func(row[i])
            journal_info_patients[study_id] = patient_dict
    
    return journal_info_patients





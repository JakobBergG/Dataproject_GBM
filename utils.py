import SimpleITK as sitk
from datetime import datetime
import re
import csv


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

    # these following columns should be read
    to_read = {
        "Study_ID",
        "MRIDiagDate_checked",
        "MRIPostopDate_checked",
        "RT_MRIDate",
        "Age_at_diagn",
        "Sex"
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
                    patient_dict[name] = row[i]
            journal_info_patients[study_id] = patient_dict
    
    return journal_info_patients

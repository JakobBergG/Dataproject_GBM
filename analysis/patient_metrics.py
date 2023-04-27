import os
from datetime import datetime
import common.utils as utils
import SimpleITK as sitk
import common.metrics as metrics
import json
import csv
import logging
import re

log = logging.getLogger(__name__)

# TODO: replace print with logging

# TODO: LOAD FROM settings.json
MINIMUM_VOXELS_LESION = 20 # if lesions contain fewer voxels than this, do not
                           # per-lesion metrics.   

TIME_POINTS = ("time0", "time1", "time2", "time3")

journal_info_path = os.path.join(utils.get_path("path_info"), "gbm_treatment_info.csv")
output_path = "" # path of where to output the end metrics file - is specified in setup()

local_path_gtv = utils.get_path("local_path_moved_gtv") #points to gtv subfolder starting from patient folder
basepath = utils.get_path("path_data")

journal_info_patients : dict = {} #dictionary with journal info - is specified in setup()

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
            patient_journal = {}
            for i, name in enumerate(names):
                if name == "Study_ID":
                    study_id = f"{row[i]:>04}" #pad with 4 zeros
                elif name in to_read:
                    func = to_read[name]
                    patient_journal[name] = func(row[i])
            journal_info_patients[study_id] = patient_journal
    
    return journal_info_patients


def get_patient_metrics(patientfolder, journal_info : dict) -> dict:
    '''Returns dictionary with metrics calculated for all time points
    Dictionary journal_info should contain information read from the .csv file
    '''
    # Load all GTVs 
    
    gtv_path = os.path.join(patientfolder, local_path_gtv)
    gtv_filelist =[ f.path for f in os.scandir(gtv_path) if f.is_file() ]
    gtvlist = []

    for pathstr in gtv_filelist:
        if os.path.basename(pathstr).endswith('_gtv.nii.gz'):
            gtvlist.append(pathstr)

    # check if no CT scan. if this is the case, stop
    # assume no CT to start with
    has_CT = False
    # also get rtdose filename
    rtdose_filename = ""

    base_filelist = [ f.path for f in os.scandir(patientfolder) if f.is_file() ]
    for pathstr in base_filelist:
        if os.path.basename(pathstr).endswith('_RTDOSE_res.nii.gz'):
            rtdose_filename = pathstr
        if os.path.basename(pathstr).endswith('CT_res.nii.gz'):
            has_CT = True

    if not has_CT:
        log.error(f"No CT scan for patient {patient_id}")
        raise Exception(f"No CT scan for patient {patient_id}")

    # -----------------------------
    # CREATE DICTIONARY FOR PATIENT
    # -----------------------------

    # Extract date information from filenames
    scans = {} # TODO fix name
    for gtv in gtvlist:
        filename = os.path.basename(gtv)
        patient_id, date, scantype, datatype = utils.parse_filename(filename)
        scans[date] = gtv #save the path for the date

    # sort based on dates (earliest scan first) # TODO remove
    dates = sorted(scans.keys())

    info = {
        "rtdose_filename": rtdose_filename,
        "flags": [] # warning messages etc. can be appended to this list
    }

    def write_timepoint(timepoint, date):
        # TODO write docstring
        if date in scans:
            filename = scans[date]
            info[timepoint] = {
                "time": date,
                "filename": filename
            }
        else:
            log.warning(f"Date for {timepoint} does not have matching scan")
            info["flags"].append("bad_date_match")
            
           

    # add subdictionary for each time point which can be filled with metric values
    # assign a timepoint to each date

    # now match times with dates from journal, if they exist (and if journal exists)

    if journal_info is None: # stop if missing journal info
        log.error(f"No journal info for patient {patient_id}")
        raise Exception(f"No journal info for patient {patient_id}")
    else:
        time0_date = journal_info["MRIDiagDate_checked"]
        time1_date = journal_info["MRIPostopDate_checked"]
        time2_date = journal_info["RT_MRIDate"]
        time3_date = journal_info["ProgressionDate"]
        
        
        if time0_date != "#NULL!":
            date0 = datetime.strptime(time0_date, "%d.%m.%Y")
            write_timepoint("time0", date0)
        if time1_date != "#NULL!":
            date1 = datetime.strptime(time1_date , "%d.%m.%Y")
            write_timepoint("time1", date1)
        if time2_date != "#NULL!":
            date2 = datetime.strptime(time2_date, "%d.%m.%Y")
            write_timepoint("time2", date2)
        if time3_date != "#NULL!":
            date3 = datetime.strptime(time3_date , "%d.%m.%Y")
            write_timepoint("time3", date3)

   
    # Check if scan exists at time2 and 3
    # for each time point, update time value to use relative time to time2 (in days)
    # warning if we are missing a time point.
    if "time3" not in info:
        return "no_recurrence_scan" # TODO: logging and errors
    elif "time2" not in info:
        return "no_baseline_scan"
    else:
        base_date = info["time2"]["time"]
        for timepoint in TIME_POINTS:
            if timepoint in info:
                info[timepoint]["time"] = utils.date_to_relative_time(info[timepoint]["time"], base_date)
            else:
                print(f"Warning: missing time point {timepoint} for patient {patient_id}")
                info["flags"].append(f"no_{timepoint}")

    # save information from journal info
    if journal_info is not None: # TODO not necessary
        for key, value in journal_info.items():
            info[key] = value
    

    # -----------------------------
    # CALCULATE METRICS FOR PATIENT
    # -----------------------------

    for timepoint in TIME_POINTS:
        if timepoint not in info:
            continue

        timepoint_info = info[timepoint]
        gtv = sitk.ReadImage(timepoint_info["filename"])

        # total volume cc
        timepoint_info["total_volume_cc"] = metrics.volume_mask_cc(gtv)

        # number of lesions
        label_image, n_normal_lesions, n_tiny_lesions = metrics.label_image_connected_components(gtv, MINIMUM_VOXELS_LESION)
        timepoint_info["n_normal_lesions"] = n_normal_lesions
        timepoint_info["n_tiny_lesions"] = n_tiny_lesions

        # volume per lesion.
        timepoint_info["lesion_volumes"] = metrics.volume_component_cc(label_image)
        
        if timepoint == "time3":
            # target dose. 
            target_dose = metrics.get_target_dose(gtv)
            info["target_dose"] = target_dose
            # Check if target dose matches journal
            if "RTdoseplan" in info:
                info["target_dose_correct"] = target_dose == info["RTdoseplan"]
            
            # 95% percentage overlap 
            rtdose = sitk.ReadImage(info["rtdose_filename"])
            gtv_resliced = utils.reslice_image(gtv, rtdose, is_label = True)
            dose_95 = metrics.dose_percentage_region(rtdose, target_dose, 0.95)
            percentage = metrics.mask_overlap(gtv_resliced, dose_95)
            if percentage == -1.0:
                print(f"Warning: gtvvolume is 0 at time 3") # TODO logging and exceptions
                info["flags"].append(f"empty_gtv_time3")
            else:
                timepoint_info["percent_overlap_95_isodose"] = percentage
            
            # Type of reccurence TODO spell recurrence right
            label_image_resliced = utils.reslice_image(label_image, rtdose, is_label = True)
            reccurence_type = metrics.type_reccurence(label_image_resliced, dose_95)
            info["reccurence_type_guess"] = reccurence_type
            # see if matches with Anouks progression type
            if "ProgressionType" in info:
                info["reccurence_type_correct"] = reccurence_type == info["ProgressionType"]
            
            # Hausdorff
            gtv_baseline = sitk.ReadImage(info["time2"]["filename"])
            
            hd, hd95 = metrics.get_hd(gtv_baseline, gtv)
            timepoint_info["hd"] = hd
            timepoint_info["hd95"] = hd95
        
    # TODO maybe not its own function?
    info = metrics.growth(info)
    
    return info
    

def setup(output_name : str):
    '''
    Load patient journal info and setup path for output
    '''
    global journal_info_patients
    global output_path
    journal_info_patients = load_journal_info_patients(journal_info_path)
    output_path = os.path.join(utils.get_path("path_output"), output_name)


def run_patient_metrics(patient_folder : str):
    '''
    Open the .json file with path metrics_path, calculate the metrics, add them
    to the .json file at output_name, and save it again
    '''
    # load journal info for all patients
    
    patient_id = os.path.basename(patient_folder)
    log.info(f"\nCalculating metrics for patient {patient_id}")
    if patient_id in journal_info_patients:
        journal_info = journal_info_patients[patient_id]
    else:
        journal_info = None

    # calculate metrics
    patient_dict = get_patient_metrics(patient_folder, journal_info)
    
    # open file to get old dict
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                info_patients = json.load(f)
            except json.decoder.JSONDecodeError: # happens if file is empty
                info_patients = {}
    else:
        info_patients = {}
    
    # add to dict
    info_patients[patient_id] = patient_dict

    # overwrite file
    with open(output_path, "w+", encoding="utf-8") as f:
        json.dump(info_patients, f, ensure_ascii=False, indent = 4)


print("All done.")


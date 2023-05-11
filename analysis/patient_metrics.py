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



MINIMUM_VOXELS_LESION = utils.get_setting("minimum_lession_size") # if lesions contain fewer voxels than this, do not
                           # per-lesion metrics.   

TIME_POINTS = ["time0", "time1", "time2", "time3"]

journal_info_path = utils.get_path("path_info")
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
        "MRIDiagDate_checked": str,     # time 0
        "MRIPostopDate_checked": str,   # time 1
        "RT_MRIDate": str,              # time 2
        "ProgressionDate": str,         # time 3
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


def get_patient_metrics(patientfolder : str, journal_info : dict) -> dict:
    '''Returns dictionary with metrics calculated for all time points for a single patient
    Dictionary journal_info should contain information read from the .csv file
    '''
    patient_id = os.path.basename(patientfolder)
    output_patient_folder = utils.get_output_patient_path(patient_id)
    
    # Load all GTVs 
    
    gtv_path = os.path.join(output_patient_folder, local_path_gtv)
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

    # Extract date information from gtv filenames and save in dictonary
    date_dic = {} 
    for gtv in gtvlist:
        filename = os.path.basename(gtv)
        patient_id, date, scantype, datatype = utils.parse_filename(filename)
        date_dic[date] = gtv #save the path for the date


    info = {
        "rtdose_filename": rtdose_filename,
        "flags": [] # warning messages etc. can be appended to this list
    }

    def write_timepoint(timepoint, date):
        '''Checks if input date has a matching scan and saves the matching 
        filname at input timepoint in dictionary.
        If no matching scan is found a warning is raised'''
        if date in date_dic:
            filename = date_dic[date]
            info[timepoint] = {
                "time": date,
                "filename": filename
            }
        else:
            log.warning(f"Date for {timepoint} does not have matching scan")
            info["flags"].append(f"bad_date_match_at_{timepoint}")
            
           

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
    # Raise error if scan at baseline or recurrence is missing.
    # warning if we are missing a scan at another timepoint.
    if "time3" not in info:
        log.error("No scan found at recurrence timepoint for patient {patient_id}")
        raise Exception("No scan found at recurrence timepoint for patient {patient_id}")
    elif "time2" not in info:
        log.error("No scan found at baseline for patient {patient_id}")
        raise Exception("No scan found at baseline for patient {patient_id}")
    else:
        base_date = info["time2"]["time"]
        for timepoint in TIME_POINTS:
            if timepoint in info:
                info[timepoint]["time"] = utils.date_to_relative_time(info[timepoint]["time"], base_date)
            else:
                log.warning(f"Warning: missing time point {timepoint} for patient {patient_id}")
                info["flags"].append(f"no_{timepoint}")
                TIME_POINTS.remove(timepoint)

    # save information from journal info
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
            rtdose = sitk.ReadImage(info["rtdose_filename"])
            target_dose = metrics.get_target_dose(rtdose)
            info["target_dose"] = target_dose
            # Check if target dose matches journal
            if "RTdoseplan" in info:
                info["target_dose_correct"] = target_dose == info["RTdoseplan"]
            
            # 95% percentage overlap 
            gtv_resliced = utils.reslice_image(gtv, rtdose, is_label = True)
            dose_95 = metrics.dose_percentage_region(rtdose, target_dose, 0.95)
            try:
                percentage = metrics.mask_overlap(gtv_resliced, dose_95)
                timepoint_info["percent_overlap_95_isodose"] = percentage
                info["classical_recurrence_type"] = metrics.classical_type_recurrence(percentage)
            except Exception as e:
                log.error(f"{str(e)} at timepoint {timepoint}")
                raise Exception(f"{str(e)} at timepoint {timepoint}")
            
            #Classical type of recurrence
            
            
            
            # Find baseline gtv
            gtv_baseline = sitk.ReadImage(info["time2"]["filename"])
            
            # Type of recurrence 
            label_image_resliced = utils.reslice_image(label_image, gtv_baseline, is_label = True)
            recurrence_type = metrics.type_recurrence(label_image_resliced, gtv_baseline)
            info["recurrence_type_guess"] = recurrence_type
            # see if matches with Anouks progression type
            if "ProgressionType" in info:
                info["recurrence_type_correct"] = recurrence_type == info["ProgressionType"]
            
            # Hausdorff
            hd, hd95 = metrics.get_hd(gtv_baseline, gtv)
            timepoint_info["hd"] = hd
            timepoint_info["hd95"] = hd95
        
    # Calculate growth and growth rate between timpoints
    # Find first available scan and baseline scan and use as baselines
    first_time = TIME_POINTS[0]
    first_time_stamp = info[first_time]["time"]
    first_cc = info[first_time]["total_volume_cc"]
    baseline_cc = info["time2"]["total_volume_cc"]
    
    if first_cc == 0.0:
        log.warning(f"Volume of first available gtv is 0 for patient {patient_id}") 
        info["flags"].append("first_cc_zero")
    elif baseline_cc == 0.0: #
        log.warning(f"Volume of baseline gtv is 0 for patient {patient_id}")
        info["flags"].append("baseline_cc_zero")
    else:
        for i in TIME_POINTS:
            stamp = info[i]["time"]
            time_dif = stamp - first_time_stamp
            cc = info[i]["total_volume_cc"]
            
            if time_dif > 0: # if not first time stamp
                growth_since_first_scan = (cc-first_cc)/first_cc
                daily_growth_since_first_scan = growth_since_first_scan/time_dif
                info[i]["growth_since_first_scan"] = growth_since_first_scan
                info[i]["daily_growth_since_first_scan"] = daily_growth_since_first_scan

            if stamp != 0.0: # if not baseline
                growth_since_baseline = (cc-baseline_cc)/baseline_cc
                daily_growth_since_baseline = growth_since_baseline/stamp
                info[i]["growth_since_baseline"] = growth_since_baseline
                info[i]["daily_growth_since_baseline"] = daily_growth_since_baseline


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
    
    log.info(f"Metrics calculated for patient {patient_id}")


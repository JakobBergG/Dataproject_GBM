import os
from datetime import datetime
import utils
import SimpleITK as sitk
import metrics
import json

SAVE_AS_JSON = True
MINIMUM_VOXELS_LESION = 20 # if lesions contain fewer voxels than this, do not
                           # per-lesion metrics.   

TIME_POINTS = ("time0", "time1", "time2", "time3")

JOURNAL_INFO_PATH = os.path.join(utils.get_path("path_info"), "gbm_treatment_info.csv")
OUTPUT_PATH = os.path.join(utils.get_path("path_output"), "patient_metrics.json")

local_path_gtv = utils.get_path("local_path_gtv") #points to gtv subfolder starting from patient folder

basepath = utils.get_path("path_data")



def get_patient_metrics(patientfolder, journal_info : dict) -> dict:
    '''Returns dictionary with metrics calculated for all time points
    Dictionary journal_info should contain information read from the .csv file
    '''
    # Load all GTVs in MR_TO_CT folder
    
    CT_path = os.path.join(patientfolder, local_path_gtv)
    CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
    gtvlist = []

    for pathstr in CT_filelist:
        if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
            gtvlist.append(pathstr)

    # also get rtdose filename
    rtdose_filename = ""

    base_filelist = [ f.path for f in os.scandir(patientfolder) if f.is_file() ]
    for pathstr in base_filelist:
        if os.path.basename(pathstr).endswith('_RTDOSE_res.nii.gz'):
            rtdose_filename = pathstr

    # -----------------------------
    # CREATE DICTIONARY FOR PATIENT
    # -----------------------------

    # Extract date information from filenames
    scans = {}
    for gtv in gtvlist:
        filename = os.path.basename(gtv)
        patient_id, date, scantype, datatype = utils.parse_filename(filename)
        scans[date] = gtv #save the path for the date

    # sort based on dates (first scan first)
    dates = sorted(scans.keys())

    info = {
        "rtdose_filename": rtdose_filename,
        "flags": [] # warning messages etc. can be appended to this list
    }

    def write_timepoint(timepoint, date):
        if date in scans:
            filename = scans[date]
            info[timepoint] = {
                "time": date,
                "filename": filename
            }
        else:
            print(f"Warning: Date for {timepoint} does not have matching scan")
            info["flags"].append("date_bad_match")

    # add subdictionary for each time point which can be filled with metric values
    # assign a timepoint to each date (we assume we have time3 and time2 always,
    # so fill these out first
    for timepoint, date in zip(reversed(TIME_POINTS[2:]), reversed(dates)):
        write_timepoint(timepoint, date)

    base_date = info["time2"]["time"]

    # now match times with time0 and/or time1 from journal, if they exist (and if journal exists)

    if journal_info is None: # add warning if missing journal info
        print(f"Warning: missing journal info for patient {patient_id}")
        info["flags"].append("no_journal")
    else:
        time0_date = journal_info["MRIDiagDate_checked"]
        time1_date = journal_info["MRIPostopDate_checked"]
        
        if time0_date != "#NULL!":
            date0 = datetime.strptime(time0_date, "%d.%m.%Y")
            write_timepoint("time0", date0)
        if time1_date != "#NULL!":
            date1 = datetime.strptime(time1_date , "%d.%m.%Y")
            write_timepoint("time1", date1)
            

    # for each time point, update time value to use relative time to time2 (in days)
    # warning if we are missing time 0 or time1
    for timepoint in TIME_POINTS:
        if timepoint in info:
            info[timepoint]["time"] = utils.date_to_relative_time(info[timepoint]["time"], base_date)
        else:
            print(f"Warning: missing time point {timepoint} for patient {patient_id}")
            info["flags"].append(f"no_{timepoint}")

    # save information from journal info
    if journal_info is not None:
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

        # volume per lesion
        timepoint_info["lesion_volumes"] = metrics.volume_component_cc(label_image)
        
        if timepoint == "time3":
            # target dose. TODO: Check against database
            target_dose = metrics.get_target_dose(gtv)
            timepoint_info["target_dose"] = target_dose

            # 95% percentage overlap (if time is time3)
            rtdose = sitk.ReadImage(info["rtdose_filename"])
            gtv_resliced = utils.reslice_image(gtv, rtdose, is_label = True)
            dose_95 = metrics.dose_percentage_region(rtdose, target_dose, 0.95)
            percentage = metrics.mask_overlap(gtv_resliced, dose_95)
            timepoint_info["percent_overlap_95_isodose"] = percentage
            
            # Type of reccurence
            label_image_resliced = utils.reslice_image(label_image, rtdose, is_label = True)
            reccurence_type = metrics.type_reccurence(label_image_resliced, dose_95)
            timepoint_info["reccurence_type"] = reccurence_type
            
            # Hausdorff
            gtv_baseline = sitk.ReadImage(info["time2"]["filename"])
            
            hd, hd95 = metrics.get_hd(gtv_baseline, gtv)
            timepoint_info["hd"] = hd
            timepoint_info["hd95"] = hd95
        
    
    info = metrics.growth(info)
    
    return info
    

# load journal info for patiens
journal_info_patients = utils.load_journal_info_patients(JOURNAL_INFO_PATH)
patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]

info_patients = {} # create dictionary to hold metrics for all patients
for patient in patientfolders:
    patient_id = os.path.basename(patient)
    print(f"\n------ Calculating metrics for patient {patient_id} ------")
    if patient_id in journal_info_patients:
        journal_info = journal_info_patients[patient_id]
    else:
        journal_info = None

    info_patients[patient_id] = get_patient_metrics(patient, journal_info)

print("All done.")

if SAVE_AS_JSON:
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(info_patients, f, ensure_ascii=False, indent = 4)
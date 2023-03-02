import os
from datetime import datetime
import utils
import SimpleITK as sitk
import metrics
import json

SAVE_AS_JSON = False
MINIMUM_VOXELS_LESION = 20 # if lesions contain fewer voxels than this, do not
                           # per-lesion metrics.   

TIME_POINTS = ("time0", "time1", "time2", "time3")

basepath = os.path.join('data')



        

def get_patient_metrics(patientfolder) -> dict:
    '''Returns dictionary with metrics calculated for all time points'''
    # Load all GTVs in MR_TO_CT folder
    
    CT_path = os.path.join(patientfolder, "MR_TO_CT")
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
    dates = []
    for gtv in gtvlist:
        filename = os.path.basename(gtv)
        patient_id, date, scantype, datatype = utils.parse_filename(filename)
        dates.append(date)

    # sort based on dates (first scan first)
    dates_names = sorted(zip(dates, gtvlist))

    info = {
        "rtdose_filename": rtdose_filename,
        "flags": [] # warning messages etc. can be appended to this list
    }

    # add subdictionary for each time point which can be filled with metric values
    # assign a timepoint to each date (we assume we have time3 and time2 always,
    # so fill out in reverse order. Time1 and time0 may be wrong)
    for timepoint, date_file in zip(reversed(TIME_POINTS), reversed(dates_names)):
        date, filename = date_file
        info[timepoint] = {
            "time": date,
            "filename": filename
        }

    base_date = info["time2"]["time"]

    # for each time point, update time value to use relative time to time2 (in days)
    # warning if we are missing time 0 or time1
    for timepoint in TIME_POINTS:
        if timepoint in info:
            info[timepoint]["time"] = utils.date_to_relative_time(info[timepoint]["time"], base_date)
        if timepoint not in info:
            print(f"Warning: missing time point {timepoint} for patient {patient_id}")
            info["flags"].append(f"no_{timepoint}")

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
    return info
    

patientfolders = [f.path for f in os.scandir(basepath) if f.is_dir()]

info_patients = {} # create dictionary to hold metrics for all patients
for patient in patientfolders:
    patient_id = os.path.basename(patient)
    print(f"Calculating metrics for patient {patient_id}")
    info_patients[patient_id] = get_patient_metrics(patient)

print("All done.")
print(info_patients)



if SAVE_AS_JSON:
    with open("patient_metrics.json", "w", encoding="utf-8") as f:
        json.dump(info_patients, f, ensure_ascii=False, indent = 4)
import os
from datetime import datetime
import utils

TIME_POINTS = ("time0", "time1", "time2", "time3")

basepath = os.path.join('data')

#Selecting only one patient (1400)
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
patient=patientfolders[3]
patientid = os.path.basename(patient)
    
# Load all GTVs in MR_TO_CT folder
CT_path = os.path.join(patient, "MR_TO_CT")
CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
gtvlist = []

for pathstr in CT_filelist:
    if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
         gtvlist.append(pathstr)

# Extract date information from filenames
dates = []
for gtv in gtvlist:
    filename = os.path.basename(gtv)
    patient_id, date, scantype, datatype = utils.parse_filename(filename)
    dates.append(date)

# sort based on dates (first scan first)
dates_names = sorted(zip(dates, gtvlist))



# assign a timepoint to each date (we assume we have time3 and time2 always,
# so fill out in reverse order. Time1 and time0 may be wrong)
info = {}
for timepoint, date_file in zip(reversed(TIME_POINTS), reversed(dates_names)):
    date, filename = date_file
    info[timepoint] = {
        "time": date,
        "filename": filename,
        "flags": [] # warning messages etc. can be appended to this list
    }

# for each time point, update time value to use relative time to time2 (in days)
base_date = info["time2"]["time"]
for timepoint in info.keys():
    info[timepoint]["time"] = utils.date_to_relative_time(info[timepoint]["time"], base_date)

# warning if we are missing time 0 or time1
for timepoint in TIME_POINTS:
    if not timepoint in info:
        print(f"Warning: missing time point {timepoint}")
        info["flags"].append(f"no_{timepoint}")


print(info)
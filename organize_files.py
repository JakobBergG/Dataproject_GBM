import os
from datetime import datetime
import utils

basepath = os.path.join('data')

#Selecting only one patient (1400)
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
patient=patientfolders[3]
patientid = os.path.basename(patient)



    
#Find GTVs
CT_path = os.path.join(patient, "MR_TO_CT")
CT_filelist =[ f.path for f in os.scandir(CT_path) if f.is_file() ]
gtvlist = []

for pathstr in CT_filelist:
    if os.path.basename(pathstr).endswith('_MR_GTV.nii.gz'):
         gtvlist.append(pathstr)

dates = []
for gtv in gtvlist:
    filename = os.path.basename(gtv)
    patient_id, date, scantype, datatype = utils.parse_filename(filename)
    dates.append(date)

times = utils.dates_to_relative_time(dates)




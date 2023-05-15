# README

Following is a description on how to use and the different steps of our data analysis pipeline which takes in radiology scans (MR and CT) from patients suffering from glioblastoma and returns an analysis of relevant metrics based on the scans.


## Description of the pipeline
The figure below illustrates the input and resulting output of each step in the pipeline. These steps are described in further detail in the sections below.

![alt text](https://gitlab.com/dcpt-research/gbm_recurrence_patterns/-/blob/seq/README_pictures/pipeline.png?raw=true)






## SETUP

### Setup and Train nn-Unet

The pipeline uses the deep learning network nn-Unet to perform brain and GTV segmentation A guide on how to setup and train a nn-Unet model, as needed in the pipeline, is found at the GitHub site for nn-Unet: https://github.com/MIC-DKFZ/nnUNet.  

### Required Data and Format
Both the MR and CT scans from the patients must be in compressed Neuroimaging Informatics Technology Initiative format also known as NIfTi. Files in this format have the following filename extension: ".nii.gz". The files further need to have the correct naming in order for the pipeline to be able to calculate the relevant metrics. The naming needs to correspond to the following structure: 

- "PATIENT-IDENTIFIER_DATE_TYPE_FILE-EXTENSION"

PATIENT-IDENTIFIER: a unique string that identifies the corresponding patient.  
DATE: the date of the given scan in the format "YYYYMMDD".  
TYPE: a string that needs to be either "MR" or "CT".  
FILE-EXTENSION: corresponding to the required file format ".nii.gz".

Finally the pipeline needs a patient journal containing clinical data for each patient. The journal should contain information about the following values:

- Patient Identifier: unique identifier for each patient.
- Diagnosis Date: date of the diagnosis scan.
- Post Operation Date: date of the postoperative scan.
- Radiotherapy Date: date of the radiotherapy planning scan.
- Recurrence Date: date of the recurrence scan.
- Radiotherapy dose: the dose of radiation given in gray (Gy). 
- Patient age: age of the patient at diagnosis.
- Sex: the gender of the patient.
- Progression type: the type of progression lesions.


### Folder Structure

In order to run the pipeline on a dataset the data of the different patients must be stored in a certain folder structure. This is necessary to ensure that the different steps in the pipeline are able to locate the needed data. The entire dataset needs to be stored in a main folder. This main folder then further needs to contain a subfolder for each patient. The names of the  different patient folders need to be distinct (e.g. patient id's), so the pipeline can separate the patients. In each patient folder the scans for the corresponding patient are stored. An example of this structure with the correct naming of the scans is shown in figure (###) below.

```
- Main/
  - 0114/
    - 0114_20230504_MR_nii.gz
    - 0114_20230507_MR_nii.gz
    - 0114_20230511_CT_nii.gz
    - 0114_20230519_MR_nii.gz
  - 3443/
    - 3443_20230625_MR_nii.gz
    - 3443_20230629_CT_nii.gz
    - 3443_20230701_MR_nii.gz
    - 3443_20230704_MR_nii.gz
```


### How to Run

To run the pipeline the repository needs to be cloned locally on the unit containing the patient data. The pipeline further needs to know where the data is stored on the local unit. The way this information is presented to the pipeline is by creating a json file called "settings.json" which is added to the repository folder and the ".gitignore" list. In this file the location of the main folder and the patient journal, as described above, should be specified as well as the wanted location for the output of the pipeline. This file further needs to specify the id of the different nn-Unet models used in the specific run of the pipeline and the dimensions of the dilation filters used in registration and skull-stripping. Lastly it also needs to specify the minimum size in voxels required for a lesion to be considered a tumor. If nothing is specified the default paths and settings defined in "utils.py" will be used. An example of such a "settings.json" file is given below.

```json
{
    # nn-Unet task IDs
    "task_id_brain_segmentation_ct":  800,
    "task_id_brain_segmentation_mr":  801,
    "task_id_gtv_segmentation": 600,

    # dilation filters
    "skull_stripping_dilation_radius_mr": [4, 4, 2], 
    "registration_dilation_radius_mr": [10, 10, 5],
    "registration_dilation_radius_ct": [5, 5, 5],

    # minimum size of lesions
    "minimum_lession_size": 20,

    # data paths
    "path_data": ".../glioblastoma/main/",
    "path_journal": "info/gbm_treatment_info.csv",
    "path_output": "output/",

}
```

When the above-mentioned process is done the pipeline can be executed by running the "pipeline.py" file. 

## Steps in Pipeline
Here follows a description of the steps in the pipeline for one patient. For each patient, the pipeline takes as input MR scans and a CT scan. The scans are 3D images as illustrated below:

ILLUSTRATION

### Brain Segmentation (MR and CT)

The first step of the pipeline is brain segmentation. The function brain_segmentation.predict_brain_masks.run_brainmask_predictions
performs the brain segmentation on the CT scan and each of the MR scans for the patient.
An illustration of an MR scan and the corresponding brain segmentation is illustrated below:

ILLUSTRATION

For each CT and MR scan the brain is segmented by nnUNet. The brain segmentations might have small objects that are not actually part of the brain mask. As a result, these small objects are removed using the function brain_segmentation.cleanup_brain_masks.cleanup_brain_mask.
A brain mask before and after cleanup is illustrated below:

ILLUSTRATION

### Skull-Stripping 

Now that a brain mask for each MR and CT scan is generated in the brain segmentation step, the function skull_stripping.strip_skull_from_mask.run_skull_stripping saves a skull-stripped version of each MR scan, i.e. everything from the scan that is not part of the brain is removed. An MR scan and its skull-stripped version is illustrated below:

ILLUSTRATION

### GTV Segmentation

In this step, each skull-stripped MR scan from the previous step is used in the function gtv_segmentation.predict_gtvs.run_prediction to segment the GTV by nnUNet.

ILLUSTRATION

### Registration MR to CT

Each MR scan is registered to the grid of the CT scan using the function registration.registration_MR_mask_to_CT_mask.register_MR_to_CT. To perform the registration using SimpleElastix, we need the brain masks from the brain segmentation step. We also need the corresponding GTV from the previous step to move along with the MR scan. The brain mask corresponding to the MR scan is also moved along with the MR scan.

ILLUSTRATION

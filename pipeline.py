import sys
import os
import common.utils as utils
import brain_segmentation.predict_brain_masks
import brain_segmentation.cleanup_brain_masks
import skull_stripping.strip_skull_from_mask
import gtv_segmentation.predict_gtvs
import logging
from datetime import datetime

# setup of logging
log_output = utils.get_path("path_output")
log_name = f"log_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.txt"
log_path = os.path.join(log_output, log_name)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))


def run_pipeline(patient_folder : str):
    '''
    Runs the pipeline for the patient with the patient folder with file path
      patient_folder.
    '''
    patient_id = os.path.basename(patient_folder)

    #
    # BRAIN SEGMENTATION
    #
    # TODO: load these values from settings.json
    log.info(f"Starting brain segmentation for patient {patient_id}")
    brain_segmentation.predict_brain_masks.setup_prediction(nnUNet_ct_task_id=800, nnUNet_mr_task_id=801)

    try:
        brain_segmentation.predict_brain_masks.run_ct_prediction(patient_folder)
    except:
        log.error(f"CT brain mask prediction failed. Stopping here for patient {patient_id}")
        return
    
    try:
        brain_segmentation.predict_brain_masks.run_mr_prediction(patient_folder)
    except:
        log.error(f"MR brain mask prediction failed. Stopping here for patient {patient_id}")
        return

    #
    # CLEANING BRAIN MASKS
    #
    log.info(f"Cleaning brain masks for patient {patient_id}")
    try:
        brain_segmentation.cleanup_brain_masks(patient_folder)
    except:
        log.error(f"Brain mask cleaning failed. Stopping here for patient {patient_id}")
        return
    
    # 
    # SKULL-STRIPPING
    #
    log.info(f"Beginning skull-stripping for patient {patient_id}")
    try:
        skull_stripping.strip_skull_from_mask.run_skull_stripping(patient_folder)
    except:
        log.error(f"Skull-stripping failed. Stopping here for patient {patient_id}")
        return

    #
    # GTV segmentation
    #
    log.info(f"Starting GTV segmentation for patient {patient_id}")
    try:
        gtv_segmentation.predict_gtvs.run_prediction(patient_folder)
    except:
        log.error(f"GTV-segmentation failed. Stopping here for patient {patient_id}")
        return





def main():
    # Load the base data path from the settings.json file
    basepath = utils.get_path("path_data")

    # Find all the patient folders in the main data folder
    patient_folders = [f.path for f in os.scandir(basepath) if f.is_dir()]
    for patient_folder in patient_folders:
        patient_id = os.path.basename(patient_folder)
        # Execute the entire pipeline for the patient
        log.info(f"Starting pipeline execution for patient {patient_id}")
        run_pipeline(patient_folder)


if __name__ == "__main__":
    sys.exit(main())
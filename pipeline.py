import sys
import os
import logging
from datetime import datetime
import common.utils as utils
import brain_segmentation.predict_brain_masks
import brain_segmentation.cleanup_brain_masks
import skull_stripping.strip_skull_from_mask
import gtv_segmentation.predict_gtvs
import registration.registration_MR_mask_to_CT_mask
import registration.mask_registration_evaluation
import analysis.patient_metrics


# setup of logging
log_output = utils.get_path("path_output")
date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_name = f"log_{date_str}.txt"
log_path = os.path.join(log_output, log_name)
logging.basicConfig(filename=log_path, level=logging.DEBUG, 
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

    try:
        brain_segmentation.predict_brain_masks.run_ct_prediction(patient_folder)
    except Exception as e:
       log.error(f"CT brain mask prediction failed for {patient_id}. Error message: {str(e)}")
       return
    
    try:
        brain_segmentation.predict_brain_masks.run_mr_prediction(patient_folder)
    except Exception as e:
        log.error(f"MR brain mask prediction failed for {patient_id}. Error message: {str(e)}")
        return

    #
    # CLEANING BRAIN MASKS
    #
    log.info(f"Cleaning brain masks for patient {patient_id}")
    try:
        brain_segmentation.cleanup_brain_masks.cleanup_brain_mask(patient_folder)
    except Exception as e:
        log.error(f"Brain mask cleaning failed for {patient_id}. Error message: {str(e)}")
        return
    
    # 
    # SKULL-STRIPPING
    #
    log.info(f"Beginning skull-stripping for patient {patient_id}")
    try:
        skull_stripping.strip_skull_from_mask.run_skull_stripping(patient_folder)
    except Exception as e:
        log.error(f"Skull-stripping failed for {patient_id}. Error message: {str(e)}")
        return

    #
    # GTV segmentation
    #
    log.info(f"Starting GTV segmentation for patient {patient_id}")
    try:
        gtv_segmentation.predict_gtvs.run_prediction(patient_folder)
    except Exception as e:
        log.error(f"GTV-segmentation failed for {patient_id}. Error message: {str(e)}")
        return
    
    #
    # REGISTRATION (MR to CT)
    #
    log.info(f"Starting registration for patient {patient_id}")
    try:
        registration.registration_MR_mask_to_CT_mask.register_MR_to_CT(patient_folder)
    except Exception as e:
        log.error(f"Registration failed for {patient_id}. Error message: {str(e)}")
        return
    
    try:
        registration.mask_registration_evaluation.add_msd_to_json(patient_folder)
    except Exception as e:
        log.error(f"Registration evaluation failed for {patient_id}. Error message: {str(e)}")
        log.info("Continuing despite mask registration fail...")
    
    #
    # Calculate metrics
    #
    log.info(f"Calculating metrics for patient {patient_id}")
    try:
        analysis.patient_metrics.run_patient_metrics(patient_folder,
                                    f"patient_metrics{date_str}.json")
    except Exception as e:
        log.error(f"Calculating patient metrics failed for {patient_id}. Error message: {str(e)}")
        return


def main():
    # Load the base data path from the settings.json file
    basepath = utils.get_path("path_data")
    # Run setup
    brain_segmentation.predict_brain_masks.setup_prediction(nnUNet_ct_task_id=800, nnUNet_mr_task_id=801)
    analysis.patient_metrics.setup(f"patient_metrics_{date_str}.json")
    # Find all the patient folders in the main data folder
    patient_folders = [f.path for f in os.scandir(basepath) if f.is_dir()]
    run_pipeline(patient_folders[0])
    # for patient_folder in patient_folders:
    #     patient_id = os.path.basename(patient_folder)
    #     # Execute the entire pipeline for the patient
    #     log.info(f"Starting pipeline execution for patient {patient_id}")
    #     run_pipeline(patient_folder)


if __name__ == "__main__":
    sys.exit(main())
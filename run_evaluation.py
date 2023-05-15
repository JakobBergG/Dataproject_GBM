import sys
import os
import logging
from datetime import datetime
import common.utils as utils
import registration.mask_registration_evaluation


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
    
    patient_id = os.path.basename(patient_folder)

    
    
    # Evaluate registraion
    registration_eval_filename = f"registration_mask_MSD_{date_str}.json"
    try:
        registration.mask_registration_evaluation.add_msd_to_json(patient_folder, registration_eval_filename)
    except Exception as e:
        log.error(f"Registration evaluation failed for {patient_id}. Error message: {str(e)}")
        log.info("Continuing despite mask registration fail...")
    
   
def main():
    # The system must be setup to allow permission to create symbolic links to
    # files. This is tested with the following function, which returns an
    # error if no permission
    utils.test_symbolic_link_permission()
    # Load the base data path from the settings.json file
    basepath = utils.get_path("path_data")
    # Run setup
    # Find all the patient folders in the main data folder
    patient_folders = [f.path for f in os.scandir(basepath) if f.is_dir()]
    # Run piepeline for all patients
    for patient_folder in patient_folders:
        patient_id = os.path.basename(patient_folder)
        # Execute the entire pipeline for the patient
        log.info(f"Starting pipeline execution for patient {patient_id}")
        run_pipeline(patient_folder)

    # Stuff to do after the pipeline has been run for all patients:

    # Sort MSD dictionary by average MSD
    registration_eval_filename = f"registration_mask_MSD_{date_str}.json"
    try:
        registration.mask_registration_evaluation.sort_msd_dict(registration_eval_filename)
    except Exception as e:
        log.error(f"MSD dictionary sort failed. Error message: {str(e)}")

    # Save histogram plot of MSD values
    msd_histogram_filename = f"MSD_histogram_{date_str}.png"
    try:
        registration.mask_registration_evaluation.sort_msd_dict(registration_eval_filename, msd_histogram_filename)
    except Exception as e:
        log.error(f"MSD histogram plot failed. Error message: {str(e)}")
    
    

if __name__ == "__main__":
    sys.exit(main())
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
import analysis.patient_metrics_to_csv


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

    #--------------------#
    # BRAIN SEGMENTATION #
    #--------------------#
    if utils.get_setting("run_brain_segmentation"): #load from settings to see if this step should be run
        log.info(f"Starting brain segmentation for patient {patient_id}")
        nnUNet_ct_task_id = utils.get_setting("task_id_brain_segmentation_ct")
        nnUNet_mr_task_id = utils.get_setting("task_id_brain_segmentation_mr")
        try:
            brain_segmentation.predict_brain_masks.run_brainmask_predictions(patient_folder, nnUNet_ct_task_id, nnUNet_mr_task_id)
        except Exception as e:
            log.error(f"Brain mask prediction failed for {patient_id}. Error message: {str(e)}")
            return

    # Clean brain masks
    if utils.get_setting("run_cleanup_brain_masks"):
        log.info(f"Cleaning brain masks for patient {patient_id}")
        try:
            brain_segmentation.cleanup_brain_masks.cleanup_brain_mask(patient_folder)
        except Exception as e:
            log.error(f"Brain mask cleaning failed for {patient_id}. Error message: {str(e)}")
            return
    
    #-----------------# 
    # SKULL-STRIPPING #
    #-----------------#
    if utils.get_setting("run_skull_stripping"):
        log.info(f"Beginning skull-stripping for patient {patient_id}")
        try:
            skull_stripping.strip_skull_from_mask.run_skull_stripping(patient_folder)
        except Exception as e:
            log.error(f"Skull-stripping failed for {patient_id}. Error message: {str(e)}")
            return

    #------------------#
    # GTV segmentation #
    #------------------#
    if utils.get_setting("run_gtv_segmentation"):
        log.info(f"Starting GTV segmentation for patient {patient_id}")
        nnUNet_gtv_task_id = utils.get_setting("task_id_gtv_segmentation")
        try:
            gtv_segmentation.predict_gtvs.run_gtv_prediction(patient_folder, nnUNet_gtv_task_id)
        except Exception as e:
            log.error(f"GTV-segmentation failed for {patient_id}. Error message: {str(e)}")
            return
        
    #-------------------------#
    # REGISTRATION (MR to CT) #
    #-------------------------#
    if utils.get_setting("run_registration"):
        log.info(f"Starting registration for patient {patient_id}")
        try:
            registration.registration_MR_mask_to_CT_mask.register_MR_to_CT(patient_folder)
        except Exception as e:
            log.error(f"Registration failed for {patient_id}. Error message: {str(e)}")
            return
    
    # Evaluate registraion
    if utils.get_setting("run_registration_evaluation"):
        registration_eval_filename = f"registration_mask_MSD_{date_str}.json"
        try:
            registration.mask_registration_evaluation.add_msd_to_json(patient_folder, registration_eval_filename)
        except Exception as e:
            log.error(f"Registration evaluation failed for {patient_id}. Error message: {str(e)}")
            log.info("Continuing despite mask registration fail...")
    
    #---------------#
    # DATA ANALYSIS #
    #---------------#
    if utils.get_setting("run_data_analysis"):
        log.info(f"Calculating metrics for patient {patient_id}")
        try:
            analysis.patient_metrics.run_patient_metrics(patient_folder)
        except Exception as e:
            log.error(f"Calculating patient metrics failed for {patient_id}. Error message: {str(e)}")
            return


def main():
    #--------------------------#
    # SETUP SETTINGS AND FILES #
    #--------------------------#

    # The system must be setup to allow permission to create symbolic links to
    # files. This is tested with the following function, which returns an
    # error if no permission
    utils.test_symbolic_link_permission()
    # Load the base data path from the settings.json file
    basepath = utils.get_path("path_data")
    # Run setup
    patient_metrics_filename = f"patient_metrics_{date_str}"
    analysis.patient_metrics.setup(patient_metrics_filename + ".json")
    # Find all the patient folders in the main data folder
    all_patient_folders = [f.path for f in os.scandir(basepath) if f.is_dir()]
    if utils.get_setting("only_run_selected_patients"):
        selected_patients = utils.get_setting("selected_patients")
        patient_folders = [e for e in all_patient_folders
                            if os.path.basename(e) in selected_patients]
    else:
        # just run for all patients
        patient_folders = all_patient_folders
    patient_ids = [os.path.basename(patient_folder) for patient_folder in patient_folders]

    # Section that prints settings to user and asks if it is OK

    log.info(f'''Looking for patient folders in the input data folder:
        {os.path.abspath(utils.get_path("path_data"))}
    
    Looking for patient journal info at:
        {os.path.abspath(utils.get_path("path_info"))}

    Output will be saved to the output folder
        {os.path.abspath(utils.get_path("path_output"))}
    
    Logfile will be saved at:
        {log_path}
    ''')

    log.info(f'''\nThe following steps of the pipeline will be run:
    Brain segmentation: {utils.get_setting("run_brain_segmentation")}
    Cleanup brain masks: {utils.get_setting("run_cleanup_brain_masks")}
    Skull stripping: {utils.get_setting("run_skull_stripping")}
    GTV segmentation: {utils.get_setting("run_gtv_segmentation")}
    Registration (MR to CT): {utils.get_setting("run_registration")}
    Registration evaluation: {utils.get_setting("run_registration_evaluation")}
    Data analysis: {utils.get_setting("run_data_analysis")}
    ''')

    if utils.get_setting("only_run_selected_patients"):
        log.info(f'''\nThe pipeline will be run for the following {len(patient_ids)} patients:
        {patient_ids}
        ''')
    else:
        log.info(f"The pipeline will be run for all {len(patient_ids)} patients.")

    settings_to_print = ["task_id_brain_segmentation_ct",
                         "task_id_brain_segmentation_mr",
                         "task_id_gtv_segmentation",
                         "skull_stripping_dilation_radius_mr",
                         "registration_dilation_radius_mr",
                         "registration_dilation_radius_ct",
                         "minimum_lesion_size",
                         "path_data",
                         "path_info",
                         "path_output"
                         ]
    settings_string = ",\n".join(f"{key}: {value}" \
                                for key, value in utils.settings.items() \
                                if key in settings_to_print)
    log.info(f'''\nYou have selected the following settings: 
{settings_string}
    ''')
    log.info("(settings can be changed in settings.json)")
    print("Do you wish to run the pipeline with these settings? To continue, type: yes")
    
    if input("Continue?: ") != "yes":
        log.info("You chose not to continue. Exiting...")
        sys.exit()
    
    #--------------------------#
    # RUN THE PIPELINE         #
    #--------------------------#

    # Run pipeline for all patients
    log.info("Starting pipeline execution.")
    for patient_folder in patient_folders:
        patient_id = os.path.basename(patient_folder)
        # Execute the entire pipeline for the patient
        log.info(f"Starting pipeline execution for patient {patient_id}")
        run_pipeline(patient_folder)

    #--------------------------#
    # AFTER PIPELINE FINISHED  #
    #--------------------------#

    # Stuff to do after the pipeline has been run for all patients:

    if utils.get_setting("run_registration_evaluation"):
        # Sort MSD dictionary by average MSD
        registration_eval_filename = f"registration_mask_MSD_{date_str}.json"
        try:
            registration.mask_registration_evaluation.sort_msd_dict(registration_eval_filename)
        except Exception as e:
            log.error(f"MSD dictionary sort failed. Error message: {str(e)}")

        # Save histogram plot of MSD values
        msd_histogram_filename = f"MSD_histogram_{date_str}.png"
        try:
            registration.mask_registration_evaluation.msd_histogram(registration_eval_filename, msd_histogram_filename)
        except Exception as e:
            log.error(f"MSD histogram plot failed. Error message: {str(e)}")
    
    # Convert patient_metrics json to csv
    if utils.get_setting("run_data_analysis"):
        try:
            analysis.patient_metrics_to_csv.convert_json_to_csv(
                os.path.join(utils.get_path("path_output"), patient_metrics_filename + ".json"),
                os.path.join(utils.get_path("path_output"), patient_metrics_filename + "_flattened.csv"),
                )
        except Exception as e:
            log.error(f"Converting patient metrics json to csv failed. Error message: {str(e)}")


if __name__ == "__main__":
    sys.exit(main())
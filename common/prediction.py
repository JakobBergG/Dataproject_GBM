import logging
import subprocess
import os
import re

log = logging.getLogger(__name__)

def nnUNet_predict(task_id : int, input_folder : str, output_folder : str):
    '''
    Run the proper nnUNet command for predicting gtvs. Runs for all scans in
    input_folder
    '''
    # nnUNet_predict runs for all scans in subfolder
    command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                str(task_id), "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
                "3d_fullres"]

    log.debug(f"Running command: {command}")
    result = subprocess.run(command)
    # if returncode is not 0, something bad happened
    if result.returncode == 0:
        log.info(f"Prediction done")
    else:
        log.error(f"nnUNet prediction did not complete succesfully")
        raise Exception("nnUNet prediction did not complete succesfully")
    

def create_scan_links(patient_folder : str, destination_folder : str,
                old_file_ending : str, new_file_ending : str):
    '''
    For all files ending with 'old_file_ending' in folder patient_folder, will
    create symbolic links in a new destination folder. Each file ending will be 
    changed to 'new_file_ending'.
    nnUNet requires that all scans to be predicted are in the same folder.
    Creating symbolic links avoids copying the files, which would double the 
    file size for each patient since there would be two copies of each scan.
    '''
    # find scans ending with old_file_ending
    patient_filelist = [f.path for f in os.scandir(patient_folder)]
    scan_list = []
    for file in patient_filelist:
        if os.path.basename(file).endswith(old_file_ending):
            scan_list.append(file)   

    # now create symbolic links in destination folder,
    # also changing name to comply with nnunet input requirements
    for source in scan_list:
        oldname = os.path.basename(source)
        newname = re.sub(old_file_ending, new_file_ending, oldname)
        dest = os.path.join(destination_folder, newname)
        source_full_path = os.path.abspath(source)
        try:
            os.symlink(source_full_path, dest)
        except:
            raise Exception("Could not create symbolic link. If on Windows, check that running as administrator")


def run_prediction(scans_folder : str, scans_file_ending,
                   nnUNet_input_folder : str, nnUNet_file_ending : str,
                   nnUNet_task_id : int, output_folder : str) :
    '''
    Run predictions for the specified scans using the model specified by the
    nnUNet task_id. Note is it assumed that all relevant folders already exist.

    Arguments:
    scans_folder: The folder containing the scans on which predictions are to be made
    scans_file_ending: All files ending with this will have predictions run on them
    nnUNet_input_folder: nnUNet needs all the scans to be moved to the same folder.
        Rather than moving them, we create symbolic links in this folder
    nnUNet_file_ending: The symbolic links will have this ending
    nnUNet_task_id: The task id of the model used for prediction
    output_folder: The folder where predictions are output
    '''

    # create symbolic links used by nnUNet
    create_scan_links(scans_folder, nnUNet_input_folder,
                      scans_file_ending, nnUNet_file_ending)

    # now run prediction
    nnUNet_predict(nnUNet_task_id, nnUNet_input_folder, output_folder)
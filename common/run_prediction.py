import logging
import subprocess

log = logging.getLogger(__name__)

def nnUNet_predict(task_id : int, input_folder : str, output_folder : str):
    '''
    Run the proper nnUNet command for predicting gtvs. Runs for all scans in
    input_folder
    '''
    # nnUNet_predict runs for all scans in subfolder
    command = ["nnUNet_predict", "-i", input_folder, "-o", output_folder, "-t",
                task_id, "-f", "0", "-tr", "nnUNetTrainerV2", "-m",
                "3d_fullres"]

    log.debug(f"Running command: {command}")
    result = subprocess.run(command)
    # if returncode is not 0, something bad happened
    if result.returncode == 0:
        log.info(f"Prediction done")
    else:
        log.error(f"nnUNet prediction did not complete succesfully")
        raise Exception("nnUNet prediction did not complete succesfully")
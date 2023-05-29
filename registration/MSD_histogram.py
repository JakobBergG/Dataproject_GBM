import os
import SimpleITK as sitk
import numpy as np
import json
import common.utils as utils
import common.metrics as metrics
import logging
import matplotlib.pyplot as plt

def msd_histogram(json_filename : str, output_name: str):
    '''
    Plots a histogram of the MSD scores from the registration
    '''

    # Load dictionary from JSON file
    json_path = os.path.join(utils.get_path("path_output"), json_filename)
    with open(json_path, "r") as f:
        patient_dic : dict = json.load(f)
    
    # Get a list of MSD score for each registration, values[-1] is the average value for the patient
    scores = [msd for patient, values in patient_dic.items() for msd in values[:-1]]

    # Plot histogram and save
    plt.hist(scores, bins=100)
    plt.title("Histogram of MSD values for registrations")
    plt.xlabel("MSD score")
    plt.ylabel("Count")
    plt.xlim((0, 7))

    output_path = os.path.join(utils.get_path("path_output"), output_name)
    plt.savefig(output_path)


json_filename = "registration_mask_MSD_2023-05-25_12-47-35.json"
plot_filename = "MSD_histogram_2023-05-25_12-47-35_no_outliers.png"

msd_histogram(json_filename, plot_filename)
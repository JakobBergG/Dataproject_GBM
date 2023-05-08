import json
import csv


def convert_json_to_csv(input_json_file, output_csv_file):
    '''
    Converts a patient metrics .json file to a csv file by "flattening"
    Creates one row for each patient
    '''
    # load dictionary
    with open(input_json_file, "r", encoding="utf-8") as f:
        info_patients = json.load(f)

    # loop over entire dictionary at first once to get all the column names
    # start off with top-level names
    names : dict = {"id": 0}
    i = 1
    for patient in info_patients.values():
        for key, value in patient.items():
            if isinstance(value, (str, int, float)):
                if key not in names:
                    names[key] = i
                    i += 1

    # now get the names in the subdictionaries time0 time1, time2 etc
    for patient in info_patients.values():
        for key, value in patient.items():
            if isinstance(value, dict):
                time_prefix = key
                for suffix, val in value.items():
                    if isinstance(val, (str, int, float)):
                        new_name = time_prefix + "_" + suffix
                        if new_name not in names:
                            names[new_name] = i
                            i += 1

    # we want the lesion volumes at the end
    for time in ("time0", "time1", "time2", "time3"):
        for j in range(0, 10): # we support up to 10 potential lesion
            name = f"{time}_lesion_volume_{j}"
            names[name] = i
            i += 1


    # now we have the names and are ready to write to csv
    # "flatten" to csv file
    with open(output_csv_file, "w") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(names.keys()) # the first row should be the column names
        for patient_id, info in info_patients.items():
            row = [""] * len(names)
            patient_id = int(patient_id)
            row[0] = patient_id
            for key, value in info.items():
                if isinstance(value, (str, int, float)):
                    row[names[key]] = value
                elif isinstance(value, dict): # we are dealing with time subdictionary
                    time_prefix = key
                    for suffix, val in value.items():
                        if isinstance(val, (str, int, float)):
                            new_name = time_prefix + "_" + suffix
                            row[names[new_name]] = val
                        elif isinstance(val, list) and suffix == "lesion_volumes": 
                            for j, vol in enumerate(val):
                                vol_name = f"{time_prefix}_lesion_volume_{j}"
                                row[names[vol_name]] = vol
            writer.writerow(row)
            
            

        
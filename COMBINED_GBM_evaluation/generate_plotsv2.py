import json
import matplotlib.pyplot as plt
import numpy as np
import os

def generate_data_from_summary(summary_file, metrics_to_collect, hospital_identifier):
    # load the summary file
    with open(f"{summary_file}") as metrics_file:
        data = json.load(metrics_file)
    
    list_of_metric_dicts = data.get("results").get("all")
    
    result = {}
    for metric in metrics_to_collect:
        result[metric] = []
    
    # loop through the segmentations
    for metrics_dict in list_of_metric_dicts:
        # select the right hospitals
        test_file_base_name = os.path.basename(metrics_dict.get("test"))
        if hospital_identifier in test_file_base_name:
            # collect the right metrics
            for metric in metrics_to_collect:
                result[metric].append(metrics_dict.get("1").get(metric))
        else:
            continue
    return result


def generate_boxplot(metrics_to_plot, summary_files_to_compare, hospital_identifier, showfliers = True):
    # number of hospitals (columns)
    n_cols = len(summary_files_to_compare)
    # number of metrics (rows)
    n_rows = len(metrics_to_plot)

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, 10), sharey="row")
    col_headers = []

    # loop through the hospitals
    for i in range(n_cols):
        col_headers.append(summary_files_to_compare[i])
        # collect the metric data
        data = generate_data_from_summary(summary_files_to_compare[i], metrics_to_plot, hospital_identifier)
        j = 0
        for metric_name, val_list in data.items():
            axs[j, i].boxplot(val_list, showfliers = showfliers)
            axs[j,i]
            j += 1
    
    #axs.add_headers(fig, col_headers=col_headers, row_headers=metrics_to_plot)
    for ax, col in zip(axs[0], col_headers):
        ax.set_title(col)
    
    for ax, row in zip(axs[:,0], metrics_to_plot):
        ax.set_ylabel(row, rotation = 0, labelpad = 60, ha = "center", va = "center")
    plt.show()



# select the metrics to use in the boxplots
metrics_to_plot = ["Avg. Surface Distance", "Hausdorff Distance 95"]

summary_file1 = "D:/GBM/GBM_predictions/Task806_ANOUK_GBM/summary.json"
summary_file2 = "D:/GBM/GBM_predictions/Task809_OUH_GBM/summary.json"
summary_files_to_compare = [summary_file1, summary_file2]
hospital_identifier = "OUH"

generate_boxplot(metrics_to_plot, summary_files_to_compare, hospital_identifier)


import json
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

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
        col_headers.append(summary_files_to_compare[i].split("/")[-2])
        # collect the metric data
        data = generate_data_from_summary(summary_files_to_compare[i], metrics_to_plot, hospital_identifier)
        j = 0
        for metric_name, val_list in data.items():
            axs[j, i].boxplot(val_list, showfliers = showfliers)
            axs[j, i].yaxis.grid(True)
            axs[j, i].set(axisbelow=True)  # Hide the grid behind plot objects
            print(f"quantiles for plot ({j}, {i}): \n 0.25: {np.quantile(val_list, 0.25):.2f} \n 0.50: {np.quantile(val_list, 0.50):.2f} \n 0.75: {np.quantile(val_list, 0.75):.2f} \n mean: {np.mean(val_list):.2f}")

            j += 1
            
    #axs.add_headers(fig, col_headers=col_headers, row_headers=metrics_to_plot)
    for ax, col in zip(axs[0], col_headers):
        ax.set_title(col, fontsize = 10)
    
    for ax, row in zip(axs[:,0], metrics_to_plot):
        ax.set_ylabel(row, labelpad = 20, ha = "center", va = "center", fontsize = 10)
    fig.suptitle(f"evaluation on {hospital_identifier} test set")
    o = '_outliers' if showfliers else ""
    plt.savefig(f"{'_'.join(col_headers)}_{hospital_identifier}{o}.jpg")
    plt.show()


def generate_single_model_boxplot(summary_file, metrics_to_plot, hospital_identifiers, showfliers = True):
    # number of hospitals (columns)
    n_cols = len(hospital_identifiers)
    # number of metrics (rows)
    n_rows = len(metrics_to_plot)

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, 10), sharey="row")
    col_headers = []

    # loop through the hospitals
    for i in range(n_cols):
        #col_headers.append(summary_file.split("/")[-2])
        col_headers.append(hospital_identifiers[i])
        # collect the metric data
        data = generate_data_from_summary(summary_file, metrics_to_plot, hospital_identifiers[i])
        j = 0
        for metric_name, val_list in data.items():
            axs[j, i].boxplot(val_list, showfliers = showfliers)
            axs[j, i].yaxis.grid(True)
            axs[j, i].set(axisbelow=True)  # Hide the grid behind plot objects
            print(f"quantiles for plot ({j}, {i}): \n 0.25: {np.quantile(val_list, 0.25):.2f} \n 0.50: {np.quantile(val_list, 0.50):.2f} \n 0.75: {np.quantile(val_list, 0.75):.2f} \n mean: {np.mean(val_list):.2f}")
            j += 1
        
    for ax, col in zip(axs[0], col_headers):
        ax.set_title(col, fontsize = 10)
    
    for ax, row in zip(axs[:,0], metrics_to_plot):
        ax.set_ylabel(row, labelpad = 20, ha = "center", va = "center", fontsize = 10)
    #fig.suptitle(f"evaluation on {hospital_identifier} test set")
    fig.suptitle("evaluation of a single model")
    o = '_outliers' if showfliers else ""
    plt.savefig(f"{'_'.join(col_headers)}_{hospital_identifier}{o}.jpg")
    plt.show()






# select the metrics to use in the boxplots
metrics_to_plot = ["Avg. Surface Distance", "Hausdorff Distance 95"]

summary_file1 = "D:/GBM/GBM_predictions/Task806_ANOUK_GBM/summary.json"
summary_file2 = "D:/GBM/GBM_predictions/Task811_CUH_GBM/summary.json"
summary_file4 = "D:/GBM/GBM_predictions/Task809_OUH_GBM/summary.json"
summary_file3 = "D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble/summary.json"

summary_files_to_compare = [summary_file1, summary_file2]
#[summary_file1, summary_file2]
hospital_identifier = "CUH"

#generate_boxplot(metrics_to_plot, summary_files_to_compare, hospital_identifier, showfliers=True)
generate_single_model_boxplot(summary_file1, metrics_to_plot, ["ANOUK", "OUH", "CUH"], showfliers= True)


# fig, ax = plt.subplots(2, 1)
# i = 0
# data = generate_data_from_summary(summary_file3, metrics_to_plot, "RECURRENCE")
# for metric_name, val_list in data.items():
#         ax[i].boxplot(val_list, showfliers = True)
#         ax[i].yaxis.grid(True)
#         ax[i].set(axisbelow=True)  # Hide the grid behind plot objects
#         #axs[j,i].yaxis.set_major_locator(MultipleLocator(1))
#         print(f"quantiles for plot ({i}): \n 0.25: {np.quantile(val_list, 0.25):.2f} \n 0.50: {np.quantile(val_list, 0.50):.2f} \n 0.75: {np.quantile(val_list, 0.75):.2f} \n mean: {np.mean(val_list):.2f}")
#         i += 1

# ax[0].set_title("RECURRENCE", fontsize = 10)
# for a, row in zip(ax, metrics_to_plot):
#     a.set_ylabel(row, labelpad = 20, ha = "center", va = "center", fontsize = 10)
# plt.savefig("RECURRENCE_outliers.jpg")
# plt.show()

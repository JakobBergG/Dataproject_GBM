import json
import matplotlib.pyplot as plt
import numpy as np

def generate_hist(hospitals):
    fig, axs = plt.subplots(3, 3, figsize=(10, 10), sharex="col", sharey="col")  # 3x3 grid
    
    # Collect data from all hospitals for each metric
    all_msd = []
    all_hd = []
    all_hd95 = []

    for hospital in hospitals:
        with open(f"{hospital}_metrics.json") as metrics_file:
            data = json.load(metrics_file)
            for patient, metrics in data.items():
                all_msd.append(metrics.get("msd"))
                all_hd.append(metrics.get("hd"))
                all_hd95.append(metrics.get("hd95"))

    # Calculate common bin edges
    msd_bins = np.linspace(min(all_msd), max(all_msd), 50)
    hd_bins = np.linspace(min(all_hd), max(all_hd), 50)
    hd95_bins = np.linspace(min(all_hd95), max(all_hd95), 50)

    for i, hospital in enumerate(hospitals):
        with open(f"{hospital}_metrics.json") as metrics_file:
            data = json.load(metrics_file)
            msd = []
            hd = []
            hd95 = []
            for patient, metrics in data.items():
                msd.append(metrics.get("msd"))
                hd.append(metrics.get("hd"))
                hd95.append(metrics.get("hd95"))

        # Plot histograms with shared bin size
        axs[i, 0].hist(msd, bins=msd_bins, color='skyblue', edgecolor='black', density=True)
        axs[i, 0].set_title(f'{hospital} - MSD Histogram')
        axs[i, 0].set_ylabel('Frequency')

        axs[i, 1].hist(hd, bins=hd_bins, color='salmon', edgecolor='black', density=True)
        axs[i, 1].set_title(f'{hospital} - HD Histogram')
        axs[i, 1].set_ylabel('Frequency')

        axs[i, 2].hist(hd95, bins=hd95_bins, color='lightgreen', edgecolor='black', density=True)
        axs[i, 2].set_title(f'{hospital} - HD95 Histogram')
        axs[i, 2].set_ylabel('Frequency')

    for j, metric_name in enumerate(["MSD", "HD", "HD95"]):
        axs[0, j].set_title(metric_name + " Histogram", fontsize=14)

    plt.show()

# Example usage:
generate_hist(["AUH", "CUH", "OUH"])



# def generate_hist(hospitals):
#     combined_msd = []
#     combined_hd = []
#     combined_hd95 = []
#     for hospital in hospitals:
#         with open(f"{hospital}_metrics.json") as metrics_file:
#             data = json.load(metrics_file)
#             msd = []
#             hd = []
#             hd95 = []
#             for patient, metrics in data.items():
#                 msd.append(metrics.get("msd"))
#                 hd.append(metrics.get("hd"))
#                 hd95.append(metrics.get("hd95"))
#         combined_msd.append(msd)
#         combined_hd.append(hd)
#         combined_hd95.append(hd95)


#     fig, axs = plt.subplots(1,3, figsize = (10, 10))
#     axs[0].hist(combined_msd, histtype = "step", label = hospitals, density = True, bins = 100)
#     axs[1].hist(combined_hd, histtype = "step", label = hospitals, density = True, bins = 100)
#     axs[2].hist(combined_hd95, histtype = "step", label = hospitals, density = True, bins = 100)
#     plt.show()

# generate_hist(["AUH", "CUH", "OUH"])
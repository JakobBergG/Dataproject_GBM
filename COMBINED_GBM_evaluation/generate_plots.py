import json
import matplotlib.pyplot as plt
import numpy as np
task = "Task806_ANOUK_GBM"
with open(f"{task}_metrics.json") as metrics_file:
    data = json.load(metrics_file)

ANOUK_metrics = {}
AUH_metrics = {}
CUH_metrics = {}
OUH_metrics = {}
RECURRENCE_metrics = {}
metrics = {"ANOUK": {}, "AUH": {}, "CUH": {}, "OUH": {}, "RECURRENCE": {}}
# Sort the metrics in the respective groups and save in dict
groups = ["ANOUK", "AUH", "CUH", "OUH"]#, "RECURRENCE"]
for patient, m in data.items():
    if patient.startswith("ANOUK"):
        metrics["ANOUK"][patient] = m
    if patient.startswith("AUH"):
        metrics["AUH"][patient] = m
    if patient.startswith("CUH"):
        metrics["CUH"][patient] = m
    if patient.startswith("OUH"):
        metrics["OUH"][patient] = m
    if patient.startswith("RECURRENCE"):
        metrics["RECURRENCE"][patient] = m

fig, axs = plt.subplots(3, 4, figsize=(10, 10), sharey="row")#, sharey="col")
i = 0
#print(metrics["ANOUK"].items())
#print([val.get("hd") for key, val in metrics["CUH"].items()])
#print([val for key, val in metrics["CUH"].items()])

for group in groups:
    msd = [patient_metrics.get("msd") for key, patient_metrics in metrics[group].items()]
    hd = [patient_metrics.get("hd") for key, patient_metrics in metrics[group].items()]
    hd95 = [patient_metrics.get("hd95") for key, patient_metrics in metrics[group].items()]
    #print(msd)
    #print(hd)
    #print(hd95)
    print(f"SUCCESS FOR {group}")
    axs[0, i].boxplot(msd, showfliers=False)
    axs[1, i].boxplot(hd, showfliers=False)
    axs[2, i].boxplot(hd95, showfliers=False)
    i = i + 1

plt.show()

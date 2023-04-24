
import numpy as np
import os
import matplotlib.pyplot as plt
import json
import common.utils as utils

with open(os.path.join(utils.get_path("path_output"), "metric_MR_to_CT.json"), "r") as f:
    patient_dic : dict = json.load(f)

# List of used metrics
metriclist = ['Mattes50', 'Mattes40', 'Mattes30', 'Mattes20', 'Hist50', 'Hist40', 'Hist30',
           'Hist20', 'Zero'] 

def plot_boxplot(dic, metric):
    data = []
    patients = patient_dic.keys()
    for patient_id in patients:
        data.append(dic[patient_id][metric][-1])
    plt.boxplot(data)
    plt.savefig('output/pictures/metrics_boxplot.png')
    plt.show()
    
    
def plot_boxplots(dic, metrics):
    data = []
    patients = patient_dic.keys()
    for metric in metrics:
            L = [dic[patient_id][metric][-1] for patient_id in patients]
            data.append(L)
    plt.figure(figsize = (10,7))
    plt.boxplot(data)
    plt.xticks(list(range(1, len(metrics) + 1)), metrics, rotation = 45)
    plt.savefig('output/pictures/metrics_boxplots.png')
    plt.show()

def plot_standardized_boxplots(dic, metrics):
    data = []
    patients = patient_dic.keys()
    for metric in metrics:
        L = np.array([dic[patient_id][metric][-1] for patient_id in patients])
        L -= np.mean(L)
        L /= np.std(L)
        data.append(L)
    plt.figure(figsize = (10,7))
    plt.boxplot(data)
    plt.xticks(list(range(1, len(metrics) + 1)), metrics, rotation = 45)
    plt.savefig('output/pictures/metrics_boxplot_standardized.png')
    plt.show()

    
def plot_score_to_zero(dic, metric):
    scores = []
    zeros = []
    patients = patient_dic.keys()
    for patient_id in patients:
        scores += dic[patient_id][metric][:-1]
        zeros += dic[patient_id]['Zero'][:-1]
    
    plt.figure(figsize =(10, 7))
    plt.plot(zeros, scores, '.')
    plt.title(f'Plot of {metric} score against fraction of zeros in image')
    plt.xlabel("Fraction of zeros in image")
    plt.ylabel(f"{metric} score")
    plt.savefig(f'output/pictures/{metric}_scores_vs_fraction_of_zeros.png')
    plt.show()

plot_standardized_boxplots(patient_dic, metriclist)


sorted_scores = []
patients = patient_dic.keys()
for metric in metriclist:
    L = [(patient_dic[patient_id][metric][-1], patient_id) for patient_id in patients]
    sorted_scores.append([metric] + sorted(L))
    
    

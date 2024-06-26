_**Note:** This project builds upon and expands an earlier project and its repository made by data science students from AU in 2023. For the readme file for their project, see: `old_readme_file.md`._
_See the bottom of the new readme file (this one) for an overview of the new Python scripts developed during the current project._

_By: Alexander Caning, Jakob Berg Gøttsche, Lucas Bjerre Rasmussen, Lucas Mørup Rasmussen_
# Introduction
In this project, the goal is to analyze and predict recurrence patterns in patients with glioblastoma (GBM) - the most aggressive form of brain cancer, with a median survival time of only 15 months. The treatment consists of maximal tumor resection (removal) followed by chemotherapy and radiotherapy. For the majority of patients, the tumor will eventually recur. The recurrence can be local, distant, or combined (both local and distant) and varies between patients. The primary objective of this project is to expand an existing pipeline to predict these recurrence patterns based on data from 389 patients. This is particularly relevant because in the case of local recurrence, intensifying radiation given at the original tumor site can be considered to achieve better clinical outcomes, as opposed to a larger general treatment area in the case of distant recurrence.

* Local: The recurrent tumor overlaps with the earlier removed tumor.
* Distant: The recurrent tumor does **not** overlap with the earlier removed tumor.
* Combined: There are both local **and** distant tumors.

  <p align="center">
  <img src="readme_images/rad_near_far_tumor.png" width=50% />
  </p>
_Example of recurrence types. The red area is the original tumor while the green area is the recurrence. The left image shows local recurrence while the right image shows a distant recurrence._

**Gross tumor volume segmentation with nnUNet**

To assist in improving the prediction process, automatic segmentation of the gross tumor volume (GTV, i.e. the tumor)  at the planning phase and time of recurrence is conducted. This means less need for manual clinical delineations (manually segmenting the GTV) of both planning and recurrence and means automatic classification of ground truth needed for training the prediction models. It also allows automatic information retrieval of how much radiation the tumor residue received during radiotherapy and also how much the area of the recurrent tumor received, which can be included in the prediction model to provide better results.
An already established pipeline segments GTVs from the planning phase images, however, this project has improved such segmentation network while also implementing a network capable of segmenting the recurrent tumors.

**Radiomics**

The goal is to be able to predict whether or not a recurrence will have a distant tumor. The prediction will be made by extracting textural and shape-based quantitative metrics (radiomic features) from the ring around the GTV in the MR taken in connection with the planning of radiotherapy. The features will be used to train a logistic regression model and also an AdaBoost classifier.


# GTV segmentation | nnUNet
The goal is to train models that can segment tumors on planning MR scans (T2 scans) and MR scans with recurrence tumors. Furthermore find out if models should be created specifically for each different hospital.
This resulted in the following models/networks:
- Task806_ANOUK_GBM (Also referred to as ANOUK network)
- Task809_OUH_GBM (Finetuned ANOUK network on OUH data; also referred to as OUH-finetuned)
- Task811_CUH_GBM (Finetuned ANOUK network on CUH data; also referred to as CUH-finetuned)
- Task812_RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM (Also referred to as RECURRENCE network)

## Data
The number of available and suitable images are:
<div align="center">
  
| Type         | Training | Test |
|--------------|----------|------|
| ANOUK        | 207      | 52   |
| AUH          | 77         | 19   |
| OUH          | 130      | 32   |
| CUH          | 156      | 39   |
| RECURRENCE  | 31       | 8    |

</div>
The ANOUK data set consists of T2 images from AUH delineated by a single doctor, with special focus on precise delineation for model training. 
The AUH, OUH, and CUH data sets contain T2 MR scans with clinical delineations made by different doctors during cancer treatment and are therefore delineated less accurately.
The scans used in T2 (planning of radiotherapy) are the scans taken after the tumor was removed. The segmentations are of the GTV, therefore including the cavity.

The recurrence data are scans of recurring tumors which are delineated by the same doctor as the ANOUK data set, also with a focus on precise delineations for model training. In the recurrence scans the cavity is always excluded in the delineation. Below can be seen a delineation of a recurrence scan (left) and a T2 MR scan (right).

  <p align="center">
    <img src="readme_images/recurrence_segmentation.png" width=25% />
      <img src="readme_images/t2_segmentation.png" width=25% />
  </p>

For further details of the data, take a look at the old readme file: `old_readme_file.md`

## Metrics

To interpret the progression curves and the evaluation boxplots the following metrics are used:

* Hausdorf distance 95th percentile (HD95): A distance metric that measures the maximum of the minimum distances between the predicted segmentation and the ground truth at the 95th percentile.

* Mean surface distance (MSD): This tells us how much, on average, the surface varies between the segmentation and the ground truth. Also referred to as Average Surface Distance.

* DICE: The Dice coefficient is a measure of the similarity between two sets, A and B. The coefficient ranges from 0 to 1, where 1 indicates that the two sets are identical, and 0 indicates that the two sets have no overlap. 

DICE is very dependent on volume and therefore can be a somewhat misleading metric, but it is an easy metric to understand compared to MSD and HD95. MSD and HD95 is a better way to compare how well a model is performing, so we decided to include all three. 

## Segmenting T2 MR scans (planning MR scan)


Our goal was to segment tumors on planning MR scans. We've had different data sets available since the tumors on the MR scans in the ANOUK dataset were delineated with a focus on training models for tumor segmentation in contrast to the data sets from AUH, OUH, and CUH where there were clinical delineations from different doctors (not as precise). We trained a network only on the data from ANOUK as a baseline network to do transfer learning from, so we could explore the possibility of finetuning a network to each hospital. The ANOUK network is trained on 165 training cases (with 42 validation cases) for 1500 epochs. In the figure below a progression curve of the training can be seen:
  <p align="center">
  <img src="readme_images/progression_ANOUK_f0.png" width=75% />
  </p>

_Progression curve of training network Task806_ANOUK_GBM. The green curve is a rough estimate of the dice metric. The blue and red curves are the loss on the training and validation set respectively.
To interpret the progression curve, see under the chapter Model Training on the page:
https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1_


In the following figures, it can be seen how the different networks (ANOUK, OUH-finetuning, CUH-finetuning) perform on different test sets. We have chosen not to include AUH since there is an overlap between the test and training data between ANOUK and AUH data patientwise.
In the below boxplot, it can be seen how the single model, ANOUK-network performs on different test sets: ANOUK data's own test set, OUH's test set, and CUH's test set. (The green triangle on the boxplots denotes the mean)
  <p align="center">
  <img src="readme_images/ANOUK_on_ANOUK_OUH_CUH_edit.jpg" width=50% />
  </p> 
It can be seen that the ANOUK model performs significantly worse on the OUH and CUH test set, which is expected because of the inconsistent clinical delineations of the OUH and CUH MR scans. Therefore it is investigated if finetuning the ANOUK model to a specific hospital would result in better results.
In the figures below the performance of the two fine-tuned networks can be seen. The two networks Task809_OUH_GBM and Task011_CUH_GBM are finetuned using the original ANOUK network on the OUH and CUH data sets with a learning rate of 1e-6 for 350 epochs.
In the below boxplot, we compare the base ANOUK network to the OUH finetuned network:
  <p align="center">
  <img src="readme_images/Task806_ANOUK_GBM_vs_Task809_OUH_GBM_on_OUH_edit.jpg" width=50% />
  </p>
  
It appears that it is performing slightly worse. And therefore this finetuning wasn't successful.
In the below boxplot, we compare the base ANOUK network to the CUH finetuned network:
  <p align="center">
  <img src="readme_images/Task806_ANOUK_GBM_vs_Task811_CUH_GBM_on_CUH_edit.jpg" width=50% />
  </p>
When finetuning to CUH it looks as if the performance has increased after finetuning, since we get slightly lower values across MSD and Hausdorf and an improved dice.

A worse performance of the finetuned networks was expected since the delineations of the tumors in the OUH and CUH data sets were more inconsistent and not made with a focus on model training. 
The increased variance on the dice boxplot may be caused by the predicted tumor volumes differing since the metric is very volume-dependent. 



## Segmenting recurrence MR scans
The goal for Task812_RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM is to segment the recurrence tumors. When segmenting a recurrence tumor there are some clinical definitions of when to include the cavity and when not to, which is hard for a network to learn. Therefore we have finetuned the ANOUK network on recurrence MR scans where the cavity is always excluded, which is different from the segmentations of T2 scans. In the figure below an example of a segmentation of a recurrence tumor can be seen.

  <p align="center">
  <img src="readme_images/recurrence_segmentation.png" width=30% />
  </p>
  
To segment the recurrence MR scans the network generated from Task806_ANOUK_GBM was finetuned on a training set consisting of 39 MR scans (31 training cases and 8 test cases).
5 fold cross-validation was used in the training to optimize the model's performance. When segmenting a recurrence tumor an ensemble was created from the 5 folds. The ensemble prediction is created by averaging the 5 probability maps (one for each model).
Through experimenting a learning rate of 1e-6 was determined best suitable for finetuning the network. in the figure below a progression curve from one of the folds can be seen.

  <p align="center">
  <img src="readme_images/progress_t812_f_3.png" width=75% />
  </p>

## Results
After finetuning the network it can be seen that the cavity is now excluded from the segmentations. (see figure below)
<p align="center">
  <img src="readme_images/RECURRENCE_recurrence_prediction.PNG" width=25% />
    <img src="readme_images/ANOUK_recurrence_prediction.png" width=25% />
</p>
The left figure is the prediction from the finetuned network and the right figure is the prediction from the ANOUK network.
Below is an illustration of the ensemble prediction from the RECURRENCE network:
  <p align="center">
  <img src="readme_images/ensemble.png" width=100% />
  </p>

Below is a figure illustrating performance on the recurrence test set of the finetuned network (right) compared to the original ANOUK network (left).
  <p align="center">
  <img src="readme_images/Task806_ANOUK_GBM_on_RECURRENCE_vs_Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble_on_RECURRENCE_edit.jpg" width=50% />
  </p>

It can be seen that the finetuning of the ANOUK network has been very successful.

# Radiomics
**Goal:** Be able to predict whether or not a recurrence will have a distant tumor.

This is important as being able to predict if a recurrent tumor is distant or not, may allow treatment during radiotherapy to focus on a concentrated area around the removed tumor in the case of only local recurrence, or a broader radiation area in the case of a distant recurrence.

The prediction will be made by extracting textural, shape-based, and statistical features about the ring (sphere) around the gross tumor volume (GTV, i.e. the tumor) in the MR scan made during the planning of radiotherapy.
The features are then used to fit a logistic regression model and also used to train an AdaBoost classifier.

**Process:**
* Create a CTV ring
* Extract features from MR using the ring as a region of interest
* Feature selection
* Prediction using logistic regression
* Prediction using AdaBoost

## Data
The number of available and suitable images are:
<div align="center">
  
| Class        | Amount |
|--------------|--------|
| Only local        | 274    |
| Has distant      | 115    |
| **Total**    | 389    | 

</div>

Note that the _Has distant_ class consists of patients with the distant recurrence type _and_ patients with the combined recurrence type. Recurrence types for all images are classified by a single doctor. The tumor is segmented by various doctors in their respective hospitals.

## Creating the CTV ring
Creating the CTV ring needs the following resources:
* Clinical delineation of gross tumor volume.
* MR from the planning phase of radiotherapy
* Segmentation of brain (Retrieved through pipeline)

The CTV is the GTV with some margin, here: 2 cm.

**Process of creating the ring:**
1. The largest lesion (i.e. tumor) is kept. The image can contain small parts of tumor, which will mess with the extraction of meaningful radiomic features, thus all lesser tumors are removed.
2. The area of the GTV is dilated (enlarged) by 2x2x1 cm. (This can be interpreted as dragging a sphere around the circumference of the GTV)
3. Keep the intersection of the dilated GTV and the brain mask; this ensures that the dilated GTV does not cross the anatomical boundary (i.e. the skull). Now we have the CTV.
4. The non-dilated GTV is removed from the CTV, resulting in a ring (hollow sphere) around the GTV. The final CTV ring can be seen in image B below.

<p align="center">
  <img src="readme_images/rad_GTV.png" />
    <img src="readme_images/rad_Ring.png" />
</p>

## Feature extraction
Extract features from MR using CTV as a region of interest. This is done with python
module pyradiomics. Extracted features are:
* First Order Statistics (19 features)
    + _First-order statistics describe the distribution of voxel intensities within the
image region defined by the mask through commonly used and basic metrics.
e.g. Max and mean of voxel intensities_
* Shape-based (3D) (16 features)
    + The 3D shape of the region of interest.
* Grey Level Co-occurrence Matrix (21 features)
* Grey Level Run Length Matrix (16 features)
* Gray Level Size Zone Matrix (16 features)
* Neighbouring Gray Tone Difference Matrix (5 features)

**Totalling 107 features.**
  
_The matrices are essentially textural features describing properties of the local distribution of the gray levels within the ROI based on the co-occurrence of gray levels, consecutive
sequences of pixels, or zones with the same gray level. The intensity of a pixel or voxel is
also called a grey level or grey tone._

## Feature selection
We use the Mann-Whitney U test (also called the Wilcoxon rank-sum test) to decide which features to use on the T2 data (planning phase). Here we take each feature for all of the patients and conduct the Mann-Whitney test on the 2 classes. If we do not have a significant p-value, we do not take the feature into account. To exclude multicollinearity we use Pearson's cross-correlation to test if the correlation is over 0.9. If it is, we exclude one of the features to remove the cross-correlation. 

A relatively high significance level in the Mann-Whitney test should be set, otherwise no features will be selected (no features have significant p-value). When raising the significance level to 20\% we get the following features: _Shape flatness, Minimum voxel gray level, GLDM: Small Dependence Low Gray Level Emphasis_. None of the mentioned features have correlation over the threshold of 0.9.
<p align="center">
<img src="readme_images/features_after_mannwhitney_test.png" width=100% />
</p>

_Boxplot of the 3 features' values for each class._
## Predict using logistic regression
An equal amount of images in both classes is ensured by randomly sampling several images from the _local_ recurrence class matching the amount of images in the lesser class, _distant_.

We use logistic regression to classify whether or not a patient will have a local or distant recurrence, based on the 3 features selected in the previous section.  We split the data into a train and test set, and run logistic regression on different models with combinations of the selected features, to see which model performs the best. This can be somewhat time-consuming for a lot of features. We do not achieve a prediction accuracy that is higher than what we can classify as random. However, this is expected as it does not seem from the box plots in the earlier section that the data is separable by a logistic regression curve; There seems to be no difference between the classes.

The best-performing model uses all 3 features retrieved in the feature selection section with an accuracy of 48% on the test set.

<p align="center">
<img src="readme_images/confusion_matrix_logistic_regression.png" width=50% />
</p>

_Confusion matrix showing results from the final model on the test set. Label 0 is local, and label 1 is distant._

## Predict using AdaBoost
The AdaBoost classifier can be seen as a more all-in-one solution to the classification problem. The solution we have implemented is as follows:

All features are included during training. When fitting an AdaBoost classifier, it calculates the (Gini) importance of each feature. Using 5-fold cross-validation we train a new model on each of the folds we have and get the features that is most important for AdaBoost in making its prediction. We then average the importance over all of the folds for each feature and thus gain the most important features. By predicting on the test data with different amounts of features, we found that a model using the 4 best features performed the best, however only with an accuracy of 50% on the test set. Including features: _Shape: Sphericity, glszm: Gray Level Non-Uniformity, glcm: JointEntropy, Shape: Surface-Volume Ratio_.

<p align="center">
<img src="readme_images/Feature_importance.png" width=50% />
</p>

_The Gini importance for each of the included features in the final model._

<p align="center">
<img src="readme_images/confusion_matrix_adaboost.png" width=50% />
</p>

_Confusion matrix showing results from the final model on the test set._

# Conclusion
In conclusion, this project has laid a foundation for predicting GBM recurrence patterns through segmentation and radiomics. 
Although our current prediction accuracies still need improvement, the methods developed and insights gained provide a foundation for future progress, to provide enhanced personalized treatment strategies and improved clinical outcomes for GBM patients.

---

# Appendix: Developed python scripts
## GTV segmentation | nnUNet
The relevant files are in the folders: `COMBINED_GBM_training` and `COMBINED_GBM_evaluation`.
The COMBINED_GBM_training folder consists of the below files:
* `generate_data_anouk.py`
* `generate_data_hospitals.py`
* `generate_data_recurrence.py`
* `generate_data_recurrence_dialated.py`
* `generate_dataset_json.py`
* `generate_raw_data.py`
* `generate_stripped_hospitals.py`
* `reslice_images.py`

_All the above files are used in combination to generate the raw data file for the task: Task805_COMBINED_GBM. See [nnUNet | Dataset Conversion](https://github.com/MIC-DKFZ/nnUNet/blob/nnunetv1/documentation/dataset_conversion.md) for the specific format of the data. By combining all the data sets in one task the network architecture used in all the models can be determined and all the data can be preprocessed the same to make finetuning possible._

The folder also contains the following files:
* `run_over_night_1.py`
* `run_over_night_2.py`
* `run_training_Task805_GPU_1.py`
* `run_training_Task806_GPU_0.py`
* `run_training_Task808_GPU_0.py`
* `run_training_Task809_GPU_0.py`
* `run_training_Task810_GPU_1.py`
* `run_training_Task812_GPU_1.py`

_The files above are used to train and finetune the networks.
The files run_over_night_1 and run_over_night_2 also contain some code used for prediction and evaluation of the networks._

The COMBINED_GBM_evaluation folder contains the following files:
* `RECURRENCE_GBM_ensemble.py`

_The above file contains code used to create ensemble predictions from the networks created by the 5-fold cross-validation. (This code was only used for testing - the code used to get the actual ensemble predictions on the RECURRENCE test set is in the run_over_night files._

* `generate_metrics.py`

_This file was used to compute the MSD, HD, and HD95 metrics using the folder containing the ground truth and the predictions. This file is not used anymore since nnUNet has a function for this used in run_evaluate_folder.py._

* `eval_network.py` & `run_evaluate_folder.py`

_The files above are used to make predictions from networks and evaluating the network by computing many different metrics and saving them in a summary.json file._

* `generate_plots.py` & `generate_plotsv2.py`

_The files above are used to create boxplots to compare different models' performance on test sets by using the summary.json files._

* `plot_npz.py`
  
_The file above is used to plot the probability maps used in the ensemble predictions on the RECURRENCE data._
## Radiomics
All relevant files used in radiomics can be found in the folder: `radiomics`
* `available_patients.py`

_Find patients that have been manually classified by Anouk and have valid MR scans_

* `radiomic_ADABoost_regression.py`

_Fit the AdaBoost classifier, and do prediction of recurrence types_

* `radiomic_combine_feature_sets.py`

_Combine the dataset of patients having local or distant recurrence with the dataset of combined recurrences (both a local and distant recurrence)._

* `radiomic_display_feature_differences.py`

_Display boxplots of feature values between the two classes. These are the boxplots seen in the readme._

* `radiomic_extraction.py`

_Script to extract radiomic features from MR scans using the CTV ring._

* `radiomic_find_features.py`

_A minor script to find the names of features according to their indices._

* `radiomic_get_masks.py`

_Create the CTV ring, as described in the readme._

* `radiomic_logistic_regression.py`

_Fit the data to the logistic regression model, and do prediction of recurrence types._

* `radiomic_resampling.py`

_Resample GTV delineation to the same voxel spacing as the MR scan. See the file for more info._

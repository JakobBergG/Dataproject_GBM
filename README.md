# Introduction
In this project, the goal is to analyze and predict recurrence patterns in patients with glioblastoma (GBM) - the most aggressive form of brain cancer, with a median survival time of only 15 months. The treatment consists of maximal tumor resection (removal) followed by chemotherapy and radiotherapy. For the majority of patients, the tumor will eventually recur. The recurrence can be local, distant, or combined (both local and distant) and varies between patients. The primary objective of this project is to expand an existing pipeline to predict these recurrence patterns based on data from 650 patients. This is particularly relevant because in the case of local recurrence, intensifying radiation given at the original tumor site can be considered to achieve better clinical outcomes, as opposed to a larger general treatment area in the case of distant recurrence.

* Local: The recurrent tumor overlaps with the earlier removed tumor.
* Distant: The recurrent tumor does **not** overlap with the earlier removed tumor.
* Combined: There are both local **and** distant tumors.

  <p align="center">
  <img src="readme_images/rad_near_far_tumor.png" width=50% />
  </p>
_Example of recurrence types. Red area is original tumor while green area is the recurrence. The left image shows local recurrence while right image shows a distant recurrence._

**GTV segmentation with nnUNet**

To assist in improving the prediction process, automatic segmentation of the gross tumor volume  (GTV, i.e. the tumor)  at the planning phase and time of recurrence is conducted. This means less need for manual clinical delineations (manually segmenting the GTV) of both planning and recurrence, and means automatic classification of ground truth needed for training the prediction models. It also allows automatic information retrieval of how much radiation the tumor residue recieved during radiotherapy and also how much the area of the recurrent tumor recieved, which can be included in the prediction model to provide better results.
An already established pipeline segments GTVs from the planning phase images, however this project has improved such segmentation network while also implementing a network capable of segmenting the recurrent tumors.

**Radiomics**

Prediction will be made by extracting textural and shape-based quantitative metrics (radiomic features) from the ring around the GTV in the MR taken in connection with planning of radiotherapy. The features will be used to train a logistic regression model and also an ADABoost classifier.

# GTV segmentation | nnUNet
1: kort introduktion
snak med Jasper om dette afsnit
vi vil opnå en mere præcis segmentering af tumorer. This will be used as a step to train recurrence pattern prediction?
We want to train models that are able to segment t2 MR scans (Which is the scans taken after the Tumor has been removed, so we can segement the cavity for radio therapy) and recurrence MR scans.

## Data
Number of available and suitable images are:
<div align="center">
  
| Type         | Training | Test |
|--------------|----------|------|
| ANOUK        | 207      | 52   |
| AUH          | xxx      | xx   |
| OUH          | 130      | 32   |
| CUH          | 156      | 39   |
| RECURRENCE*  | 31       | 8    |

</div>
*: RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM is the data for RECURRENCE 

what is T2 mr scan
what is ...
definition of gtv
definition of recurrence gtv
image of segmentation?

3: segmenting T2 MR scans
3.5: models:
3.5.1: anouk
3.5.2: finetuning
3.6:
compare models

  <p align="center">
  <img src="readme_images/ANOUK_on_ANOUK_OUH_CUH_edit.jpg" width=50% />
  </p>
  
  <p align="center">
  <img src="readme_images/Task806_ANOUK_GBM_vs_Task809_OUH_GBM_on_OUH_edit.jpg" width=50% />
  </p>

  <p align="center">
  <img src="readme_images/Task806_ANOUK_GBM_vs_Task811_CUH_GBM_on_CUH_edit.jpg" width=50% />
  </p>

## Segmenting recurrence MR scans
The goal for Task812_RECURRENCE... is to segment the recurrence tumors. When segmenting a recurrence tumor there are som different clinical definitions of when to include the cavity and when not to which is hard for a network to learn. Therefore we have finetuned the network on MR scans where the cavity is allways excluded, which is different from the segmentations of t2 scans. In the figure below an example of a segmentation of a recurrence tumor can be seen.

  <p align="center">
  <img src="readme_images/recurrence_segmentation.png" width=30% />
  </p>
  
To segment the recurrence MR scans the newtork generated from Task806_ANOUK_GBM was finetuned on a training set consisting of XXX MR scans (XXX training cases and XXX test cases).
5 fold cross validation was used in the training to optimize the models performance. When segmenting a recurrence tumor an ensemble is created from the 5 folds (maybe this sentence can be written better).
through experimenting a learning rate of 1e-6 was determined best suitable for finetuning the network. in the figure below a progression curve from one of the folds can be seen.

  <p align="center">
  <img src="readme_images/progress_t812_f_3.png" width=40% />
  </p>

## Results
After finetuning the network it can be seen that the cavity is now excluded from the segmentations. (see figure below)
<p align="center">
  <img src="readme_images/RECURRENCE_recurrence_prediction.PNG" width=25% />
    <img src="readme_images/ANOUK_recurrence_prediction.png" width=25% />
</p>

The performance of the network is:
  <p align="center">
  <img src="readme_images/RECURRENCE_on_RECURRENCE_edit.jpg" width=50% />
  </p>




# Radiomics
**Goal:** Be able to predict whether or not a recurrence will have a distant tumor.

This is important as being able to predict if a recurrent tumor is distant or not, may allow treatment during radiotherapy to focus on a concentrated area around the removed tumor in the case of only local recurrence, 
or a broader radiation area in the case of a distant recurrence.

Prediction will be made by extracting textural, shape-based and statistical features about the ring (sphere) around the gross tumor volume (GTV, i.e. the tumor) in the MR scan made during planning of radiotherapy.
The features are then used to fit a logistic regression model and also used to train an ADABoost classifer.

**Process:**
* Create CTV ring
* Extract features from MR using ring as region of interest
* Feature selection
* Prediction using logistic regression
* Prediction using ADABoost

## Data
Number of available and suitable images are:
<div align="center">
  
| Type         | Amount |
|--------------|--------|
| Local        | 274    |
| Distant      | 115    |
| **Total**    | 389    | 

</div>
Recurrences for all images are classified by a single doctor. The tumor is segmented by various doctors in their respective hospital. 

## Creating the CTV ring
Creating the CTV ring needs the following resources:
* Clinical delineation of gross tumor volume.
* MR from planning phase of radiotherapy
* Segmentation of brain (Retrieved through pipeline)

The CTV is the GTV with some margin, here: 2 cm.

**Process of creating the ring:**
1. The largest lesion (i.e. tumor) is kept. The image can contain small parts of tumor, which will mess with the extraction of meaningful radiomic features, thus all lesser tumor are removed.
2. The area of the GTV is dilated (enlarged) by 2x2x1 cm. (Can be interpreted as dragging a sphere around the circumfrence of the GTV)
3. Keep the intersection of the dilated GTV and the brain mask; this ensures that the dilated GTV does not cross the anatomical boundary (i.e. the skull). Now we have CTV seen in image B.
4. The non-dilated GTV is removed from the CTV, resulting in a ring (hollow sphere) around the GTV. Final CTV ring can be seen in image C.

<p align="center">
  <img src="readme_images/rad_GTV.png" />
    <img src="readme_images/rad_Ring.png" />
</p>

## Feature extraction
Extract features from MR using CTV as region of interest. This is done with python
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
  
_The matrices are essentially textural features describing properties of the local distribution of the gray levels within the ROI based on co-occurrence of gray levels, consecutive
sequence of pixels or zones with the same gray level. The intensity of a pixel or voxel is
also called a grey level or grey tone_

## Feature selection
We use the Mann-Whitney U test (also called the Wilcoxon rank-sum test) to decide which features to use on the time 2 data. Here we take each feature for all of the patients, and conduct the Mann-Whitney test on the 2 classes. If we do not have a significant p-value, we do not take the feature into account. It should be noted that we have equal number in the first class, as we have in the second class. This is important for both the selection and the prediction. To exclude multicollinearity we use the pearson's cross-correlation to test, and test weither the correlation is over 0.9. If it is, we exclude one of the features to remove the cross-correlation. 

A relative high significance level should be set, otherwise no features will be selected. When testing with a significance level of 20\% we get the following features: _Shape flatness, Minimum voxel gray level, GLDM: Small Dependence Low Gray Level Emphasis_
<p align="center">
<img src="readme_images/features_after_mannwhitney_test.png" width=100% />
</p>

## Predict using logistic regression
We use logistic regression to classify whether or not a patient will have a local or distant recurrence, based on the features we have selected from the previous section. We run logistic regression on different combinations of the index, to see which ones match the best. This can be somewhat time-consuming for a lot of indices. We split the data into a train and test set. We do not achieve a prediction accuracy that is higher than what we can classify as random. Furthermore, it does not seem from the box plots that the data is separable by a logistic regression curve.
48% accuracy.

<p align="center">
<img src="readme_images/confusion_matrix_logistic_regression.png" width=50% />
</p>


## Predict using ADABoost
The ADABoost classifier can be seen as a more all-in-one solution to the classification problem. The solution we have implemented is as follows.

First, we try to make ADABoost select the most important features, based on cross-validation. We train a new model on each of the folds we have, and get the features that is most important for ADABoost in making its prediction. We then average the importance over all of the folds and then use the top most important features. We then run ADABoost for the selected features, fit the data on a train test and then we predict on a test set. We do not observe values of anything worth writing home about, as the accuracy usually hovers around 55\%.

<p align="center">
<img src="readme_images/Feature_importance.png" width=50% />
</p>

'original_shape_Sphericity', 'original_glszm_GrayLevelNonUniformity', 'original_ngtdm_Contrast', 'original_shape_SurfaceVolumeRatio'



4 features, 50%

<p align="center">
<img src="readme_images/confusion_matrix_adaboost.png" width=50% />
</p>

# Conclusion

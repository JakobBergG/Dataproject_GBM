# Radiomics
Glioblastoma (GBM) is generally expected to reoccurs after removal of the tumor. The recurrent tumor(s) can be:
* Local: The recurrent tumor overlaps with the earlier removed tumor.
* Distant: The recurrent tumor does \textbf{not} overlap with the earlier removed tumor.
* Combined: There are both local \textbf{and} distant tumors.

**Goal:** Be able to predict whether or not a recurrence will have a distant tumor.

This is important as being able to predict if a recurrent tumor is distant or not, may allow treatment during radiotherapy to focus on a concentrated area around the removed tumor in the case of only local recurrence, 
or a broader radiation area in the case of a distant recurrence.

Prediction will be made by extracting textural, shape-based and statistical features about the ring (sphere) around the gross tumor volume (GTV, i.e. the tumor) in the MR scan made during planning of radiotherapy.
The features are then used to fit a logistic regression model and used to train an ADABoost classifer.

**Process:**
* Create CTV ring
* Extract features from MR using ring as region of interest
* Feature selection
* Prediction using logistic regression
* Prediction using ADABoost

## Data
Local: 274

Distant & Combined: 115

Total: 389

Recurrences for all images are classified by a single doctor. The tumor is segmented by various doctors in their respective hospital. 

## Creating the CTV ring
Creating the CTV ring needs the following resources:
* Clinical delineation of gross tumor volume.
* MR from planning phase of radiotherapy
* Segmentation of brain (Retrieved through pipeline)

The CTV is the GTV with some margin, here: 2 cm.

\textbf{Process of creating the ring:}
\begin{enumerate}
    \item The largest lesion (i.e. tumor) is kept. The image can contain small parts of tumor, which will mess with the extraction of meaningful radiomic features, thus all lesser tumor are removed.
    \item The area of the GTV is dilated (enlarged) by 2x2x1 cm. (Can be interpreted as dragging a sphere around the circumfrence of the GTV)
    \item Keep the intersection of the dilated GTV and the brain mask; this ensures that the dilated GTV does not cross the anatomical boundary (i.e. the skull). Now we have CTV seen in image B.
    \item The non-dilated GTV is removed from the CTV, resulting in a ring (hollow sphere) around the GTV. Final CTV ring can be seen in image C.
\end{enumerate}

\textbf{INSERT PICTURE OF CTV RING HERE}

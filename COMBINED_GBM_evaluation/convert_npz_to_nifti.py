import nibabel as nib
import numpy as np

# Input
npz_file = 'D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble_folds/fold_0/RECURRENCE_23939.npz'
# Output
nii_img_file = 'test.nii.gz'
nii_seg_file = 'test_seg.nii.gz'

data = np.load(npz_file)
print(data)
array = data["softmax"][0]
array = array.astype(dtype="float64")
# array_seg = data["seg"][0]

affine = np.eye(4)
affine = affine.astype(dtype="float64")
nifti_img = nib.Nifti1Image(array, affine)
# nifti_seg = nib.Nifti1Image(array_seg, affine)

nib.save(nifti_img, nii_img_file)
# nib.save(nifti_seg, nii_seg_file)
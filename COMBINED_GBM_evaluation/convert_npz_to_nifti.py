import nibabel as nib
import numpy as np
import nnunet.inference.segmentation_export as t
import SimpleITK as sitk

def reslice_image(itk_image : sitk.Image, itk_ref : sitk.Image , is_label : bool = False) -> sitk.Image:
    '''Reslice one image to the grid of another image (when they are registered)'''
    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(itk_ref)
    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)

# Input
npz_file = 'E:/Jasper/nnUNet/nnUNet_trained_models/nnUNet/3d_fullres/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/nnUNetTrainerV2__nnUNetPlansv2.1/fold_4/validation_raw/RECURRENCE_23989.npz'
# Output
nii_img_file = 'test.nii.gz'
nii_seg_file = 'test_seg.nii.gz'

data = np.load(npz_file)
print(data)
array = data["softmax"][0]
array = array.astype(dtype="float64")
# array_seg = data["seg"][0]


#t.save_segmentation_nifti_from_softmax()
affine = np.eye(4)
affine = affine.astype(dtype="float64")

nifti_img = nib.Nifti1Image(array, affine)
# nifti_seg = nib.Nifti1Image(array_seg, affine)

nib.save(nifti_img, nii_img_file)
# nib.save(nifti_seg, nii_seg_file)

# SKUD I TÅGEN:
image1 = "C:/Users/Student1/Desktop/GBM_code/Dataproject_GBM/test.nii"
image2 = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/imagesTr/RECURRENCE_23989_0000.nii"
a = sitk.ReadImage(image1)
b = sitk.ReadImage(image2)
c = reslice_image(a, b)
sitk.WriteImage(c,"C:/Users/Student1/Desktop/GBM_code/Dataproject_GBM/test2.nii")

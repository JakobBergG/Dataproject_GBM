import nibabel as nib
import numpy as np
import nnunet.inference.segmentation_export as t
import SimpleITK as sitk
import matplotlib.pyplot as plt



for f in [0,1,2,3,4]:
    # Input
    npz_file = f'D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble_folds/fold_{f}/RECURRENCE_24233.npz'

    data = np.load(npz_file)
    array = data["softmax"][1]

    plt.imshow(array[60])
    plt.show()
    plt.savefig(f"probability_map_f{0}.png")


array = array.astype(dtype="float64")
# array_seg = data["seg"][0]

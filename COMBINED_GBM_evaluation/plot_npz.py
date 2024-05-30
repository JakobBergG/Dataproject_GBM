import nibabel as nib
import numpy as np
import nnunet.inference.segmentation_export as t
import SimpleITK as sitk
import matplotlib.pyplot as plt

combined_pmaps = []


# Input
npz_file = f'D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble_folds/fold_0/RECURRENCE_24233.npz'

data = np.load(npz_file)
array = data["softmax"][1]
combined_pmaps.append(array)
plt.imshow(array[58],cmap="hot")
plt.colorbar()
plt.savefig(f"probability_map_f0.png")

for f in [1,2,3,4]:
    # Input
    npz_file = f'D:/GBM/GBM_predictions/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM_ensemble_folds/fold_{f}/RECURRENCE_24233.npz'

    data = np.load(npz_file)
    array = data["softmax"][1]
    combined_pmaps.append(array)
    plt.imshow(array[58],cmap="hot")
    plt.savefig(f"probability_map_f{f}.png")


combined_pmap = np.zeros_like(combined_pmaps[0])

for p_map in combined_pmaps:
    print(p_map.shape)
    combined_pmap = combined_pmap + p_map

print(combined_pmap)
combined_pmap = combined_pmap / 5
plt.imshow(combined_pmap[58], cmap="hot")
plt.savefig(f"combined_probability_map.png")
plt.show()

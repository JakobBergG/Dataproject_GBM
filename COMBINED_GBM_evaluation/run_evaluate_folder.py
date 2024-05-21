import os
import nnunet
import subprocess
import nnunet.evaluation.evaluator



dirname = 'e:\\'
main_dir = os.path.join(dirname, 'Jasper','Software','nnUNet-1','nnunet')
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

os.chdir(main_dir)
REF = "E:/Jasper/nnUNet/nnUNet_raw_data/Task812_RECURRENCE_DIALETED_CAVITY_EXCLUDED_GBM/labelsTs"
PRED = "D:/GBM/COMBINED_GBM_predictions/Task812_RECURRENCE_DIALATED_CAVITY_EXCLUDED_GBM_fold_1"
L = (1,)
#test = nnunet.evaluation.evaluator.Evaluator(test = PRED, reference=REF, labels=L, metrics)

#nnunet.evaluation.evaluator.evaluate_folder(folder_with_gts=REF, folder_with_predictions=PRED, labels = L, metric_kwargs=metrics)
# test.set_test(PRED)
# test.set_reference(REF)
# test.set_labels(L)
# test.evaluate()
# metrics = test.to_dict()
# print(metrics)
#nnunet.evaluation.evaluator.evaluate_folder(REF, PRED, L, advanced = True)
#nnUNet_train 3d_fullres nnUNetTrainerV2 TaskXXX_MYTASK FOLD --npz
command = ["nnUNet_evaluate_folder", "-ref", REF, "-pred", PRED, "-l", "1"]


subprocess.run(command)
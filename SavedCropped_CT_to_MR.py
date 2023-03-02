
# import matplotlib.pyplot as plt
import SimpleITK as sitk
import numpy as np
import os

run_Registration = True
run_nnUNet = False


#you do not have access to the nnUNet model yet, so lets skip this part
if run_nnUNet:
    # import nnunet
    dir = 'e:\\'
    main_dir = os.path.join(dir, 'Jasper','Software','nnUNet-1','nnunet')
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.chdir(main_dir)

#this function can be used to calculate the mutual information between two images.
#in our data this is a negative number, and the lower, the better the registration
def calcMI(fixed, moving):
    score = 0.0
    try:
        registration_method = sitk.ImageRegistrationMethod()
        registration_method.SetMetricAsMattesMutualInformation()
        score = registration_method.MetricEvaluate(sitk.Cast(fixed, sitk.sitkFloat32),sitk.Cast(moving, sitk.sitkFloat32))
    except:
        print('failed')
    return score

#this function can be used to slice one image to the grid of another image (when they are registered)
def reslice_image(itk_image, itk_ref, is_label=False):
    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(itk_ref)

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)


#this function finds the minimum cropbox of a scan to exclude the background (assuming that the background is set to 0)
def getCropParameters(moving, marginsize=0):
    label_shape_filter = sitk.LabelShapeStatisticsImageFilter()
    label_shape_filter.Execute(moving)
    #this will give us a bounding box with [indexX, indexY, indexZ, sizeX, sizeY, sizeZ)
    bb = label_shape_filter.GetBoundingBox(1)

    # if you want to remove some additional area to be sure the corrupt parts are out add a crop margin
    margin = marginsize
    crop = np.arange(6)
    crop[0] = bb[0]+margin
    crop[1] = bb[0]+margin+bb[3]-2*margin
    crop[2] = bb[1]+margin
    crop[3] = bb[1]+margin+bb[4]-2*margin
    crop[4] = bb[2]+margin
    crop[5] = bb[2]+margin+bb[5]-2*margin
    #return values are thus [xmin, xmax, ymin, ymax, zmin, zmax]
    return crop

#here the Elastix parameter map for rigid registration is set.
def rigidParameterMap():
    parameterMapRigid = sitk.GetDefaultParameterMap('rigid')
    
    parameterMapRigid['CheckNumberOfSamples']= ['false']
    parameterMapRigid['FixedImageDimension'] = ['3']
    parameterMapRigid['MovingImageDimension'] = ['3']
    parameterMapRigid['FixedInternalImagePixelType'] = ['float']
    parameterMapRigid['MovingInternalImagePixelType'] = ['float']
    
    parameterMapRigid['AutomaticScalesEstimation']= ['false']
    parameterMapRigid['AutomaticTransformInitialization']= ['true']
    parameterMapRigid['AutomaticTransformInitializationMethod']= ['GeometricalCenter']
    parameterMapRigid['DefaultPixelValue']= ['0.0']
    parameterMapRigid['FinalGridSpacingInVoxels']= ['10']
    parameterMapRigid['FixedImagePyramid']= ['FixedSmoothingImagePyramid']
    parameterMapRigid['HowToCombineTransforms']= ['Compose']
    parameterMapRigid['ImageSampler']= ['Random']
    parameterMapRigid['Interpolator']= ['BSplineInterpolator']
    parameterMapRigid['MaximumNumberOfIterations']= ['1000']
    parameterMapRigid['Metric']= ['AdvancedMattesMutualInformation']
    parameterMapRigid['MovingImagePyramid']= ['MovingSmoothingImagePyramid']
    parameterMapRigid['NumberOfResolutions']= ['3']
    parameterMapRigid['ImagePyramidSchedule']= ['16','16','16','8','8','8', '4','4','4']

    parameterMapRigid['NumberOfSpatialSamples']=['2048']
    parameterMapRigid['Optimizer']= ['AdaptiveStochasticGradientDescent']
    parameterMapRigid['Registration']= ['MultiResolutionRegistration']
    parameterMapRigid['ResampleInterpolator']= ['FinalBSplineInterpolator']
    parameterMapRigid['Resampler']= ['DefaultResampler']
    parameterMapRigid['ResultImageFormat']= ['nii']
    parameterMapRigid['ResultImagePixelType']= ['unsigned short']
    parameterMapRigid['UseDirectionCosines']= ['true']
    parameterMapRigid['WriteResultImage']= ['true']    
    return parameterMapRigid

dilate_filter = sitk.BinaryDilateImageFilter()
dilate_filter.SetKernelType(sitk.sitkBall)
dilate_filter.SetKernelRadius((5,5,2))
dilate_filter.SetForegroundValue(1)

os.chdir("D:\\GBM")
basepath = os.path.join("nii_preprocessed")
logfilepath = os.path.join(basepath, 'CT_to_MR.txt')
patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]

print(basepath)
for patient in patientfolders:
    patientid = os.path.basename(patient)
    outfolder = os.path.join(patient, 'CT_to_MR')
    if not os.path.isdir(outfolder):
        os.makedirs(outfolder) 
    nnUnetInputFolder = os.path.join(outfolder, 'nnUnet')
    if not os.path.isdir(nnUnetInputFolder):
        os.makedirs(nnUnetInputFolder) 
    nnUnetOutputFolder = os.path.join(outfolder, 'nnUnet_GTV')
    if not os.path.isdir(nnUnetOutputFolder):
        os.makedirs(nnUnetOutputFolder) 
    # create folder to save cropped images pr. patient
    cropfilepath = os.path.join(patient, 'CroppedImages_CT_to_MR') 
    if not os.path.isdir(cropfilepath):
        os.makedirs(cropfilepath)
    
    if run_Registration:
        f = open(logfilepath, 'a+')

        # if not(patientid=='0114'):
        #     continue

        # if run_nnUNet:
        #     outfolder_nnUNet = os.path.join(basepath,  os.path.basename(patient), 'MR_ss_GTV')
        #     if not os.path.isdir(outfolder_nnUNet):
        #         os.makedirs(outfolder_nnUNet)


        filelist = [ f.path for f in os.scandir(patient) if f.is_file() ]
        ct_file = ''
        brain_file = ''
        gtv_file = ''
        mrlist = []
        for pathstr in filelist:
            if os.path.basename(pathstr).endswith('CT_res.nii.gz'):
                ct_file = pathstr
            if os.path.basename(pathstr).endswith('CT_brain.nii.gz'):
                brain_file = pathstr
            if os.path.basename(pathstr).endswith('MR_res.nii.gz'):
                mrlist.append(pathstr)
            if os.path.basename(pathstr).endswith('CT_gtv.nii.gz'):
                gtv_file = pathstr
        if brain_file == '':
            println = patientid + '\t' + 'no brain delineation'+ '\n'
            f.write(println)  
            f.close  
            continue
        print('ctfile = ', ct_file)
        print('brainfile = ', brain_file)
        print(mrlist)
        
        mrIndex = 0 #index to match the CT image with the different mr images

        parameterMapRigid= rigidParameterMap()
        movingfilename = ct_file
        moving = sitk.ReadImage(movingfilename) 
        maskfilename = brain_file
        brainmask = sitk.ReadImage(maskfilename)
        if gtv_file != '':
            gtvmask = sitk.ReadImage(gtv_file)
            dilate_filter.SetKernelRadius((3,3,1))
            gtvmask = dilate_filter.Execute(gtvmask)
            brainmask = sitk.Clamp(brainmask + gtvmask,upperBound=1)
            dilate_filter.SetKernelRadius((5,5,2)) 
        brainmask = reslice_image(brainmask, moving,True)
        for mr in mrlist:
            
            mrIndex += 1 # get a new index pr. mr
            
            fixed = sitk.Cast(sitk.ReadImage(mr),sitk.sitkFloat32)
            fixedfilename = os.path.basename(mr)

            regfolder = outfolder  
            
            parameterMapRigid['AutomaticTransformInitialization']= ['true']
            parameterMapRigid['AutomaticTransformInitializationMethod']= ['GeometricalCenter']
            parameterMapRigid['NumberOfResolutions']= ['3']
            parameterMapRigid['ImagePyramidSchedule']= ['16','16','16','8','8','8', '4','4','4']

            elastix = sitk.ElastixImageFilter()
            elastix.SetFixedImage(fixed)
            elastix.SetMovingImage(moving)
            elastix.SetOutputDirectory(regfolder)
            elastix.SetParameterMap(parameterMapRigid)

            CTImage = elastix.Execute()
            transf0 = elastix.GetTransformParameterMap() 

            ctfilename = fixedfilename.replace('MR_', 'CT_')
            sitk.WriteImage(CTImage, os.path.join(outfolder, ctfilename))

            Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
            pre, ext = os.path.splitext(fixedfilename)
            transformstring1 = os.path.join(outfolder, pre + '_TranformRigid1.txt')
            if os.path.exists(transformstring1):
                os.remove(transformstring1)
            os.rename(Transform, transformstring1)

            parameterMapRigid['AutomaticTransformInitialization']= ['false']
            parameterMapRigid['NumberOfResolutions']= ['2']
            parameterMapRigid['ImagePyramidSchedule']= ['4','4','4', '2','2','2' ]         
            elastix.SetParameterMap(parameterMapRigid)
            elastix.SetMovingMask(brainmask)
            elastix.SetInitialTransformParameterFileName(transformstring1)
            CTImage = elastix.Execute()
            
            Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
            pre, ext = os.path.splitext(fixedfilename)
            transformstring2 = os.path.join(outfolder, pre + '_TranformRigid2.txt')
            if os.path.exists(transformstring2):
                os.remove(transformstring2)
            os.rename(Transform, transformstring2)

            # transf1 = elastix.GetTransformParameterMap()
            # sum = []
            # for i in range(0,6):
            #     sum.append(str(transf0[0]["TransformParameters"][i] +transf1[0]["TransformParameters"][i])) 
            # transf0[0]["TransformParameters"]=tuple(sum)
            # print(transf0[0]["TransformParameters"])
            # print(transf1[0]["TransformParameters"])
            # print(tuple(sum)) 

            transformix=sitk.TransformixImageFilter()
            transformix.SetMovingImage(brainmask)

            transf0[0]['FinalBSplineInterpolationOrder']=['0']
            transformfilename = fixedfilename.replace('MR_res.nii.gz', 'MR_transform.txt')
            sitk.WriteParameterFile(transf0[0], os.path.join(regfolder, transformfilename))
            transformix.SetTransformParameterMap(transf0[0])
            
            transformix.Execute()
            BrainImage = transformix.GetResultImage()

            BrainImage = sitk.Cast(BrainImage,sitk.sitkUInt8)
            brainfilename = fixedfilename.replace('MR_', 'BRAIN_')
            sitk.WriteImage(BrainImage, os.path.join(outfolder, brainfilename))

            crop = getCropParameters(BrainImage, 3)
            croppedmoving = CTImage[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
            croppedfixed = fixed[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
            score = calcMI(croppedfixed, croppedmoving)
            
            #saving croppedfixed and croppedmoving
            sitk.WriteImage(croppedmoving, os.path.join(cropfilepath, f'CT{mrIndex}_' + os.path.basename(movingfilename)))
            sitk.WriteImage(croppedfixed, os.path.join(cropfilepath, f'MR{mrIndex}_' + os.path.basename(fixedfilename)))
            
            print('score=',score)
            println = patientid + '\t' + fixedfilename + '\t' + '{:.2f}'.format(score) + '\n'
            f.write(println)
            print(println)
            BrainImage = dilate_filter.Execute(BrainImage)
            BrainImage = reslice_image(BrainImage, fixed,True)

            fixed = fixed * sitk.Cast(BrainImage,sitk.sitkFloat32)
            ss_filename =fixedfilename.replace('MR_res', 'MR_GTV_0000')  
            # sitk.WriteImage(fixed, os.path.join(outfolder, ss_filename))
            sitk.WriteImage(fixed, os.path.join(nnUnetInputFolder, ss_filename))

            del elastix
        f.close()

    if run_nnUNet:
        # from pathlib import WindowsPath
        os.chdir(main_dir)
        command = f"nnUNet_predict -i {nnUnetInputFolder} -o {nnUnetOutputFolder} -t 600 -f 0 -tr nnUNetTrainerV2 -m 3d_fullres"
        os.system(command)
        # !nnUNet_predict -i f"d:\GBM\nii_preprocessed\{patientid}\MR_ss" -o f"r'{outfolder_nnUNet}'" -t 600 -f 0 -tr nnUNetTrainerV2 -m 3d_fullres
        #nnunet.nnUNet_predict.main(["-i", outfolder_ss, "-o", outfolder_nnUNet, "-t", 600,  "-f'= 0, '-tr'=nnUNetTrainerV2, '-m'=3d_fullres])

        


# %%

# import matplotlib.pyplot as plt
import SimpleITK as sitk
import numpy as np
import os

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

#this function can be used to resampel scans to a certain grid
def resample_image(itk_image, out_spacing=[0.5, 0.5, 1.0], is_label=False):
    original_spacing = itk_image.GetSpacing()
    original_size = itk_image.GetSize()

    out_size = [
        int(np.round(original_size[0] * (original_spacing[0] / out_spacing[0]))),
        int(np.round(original_size[1] * (original_spacing[1] / out_spacing[1]))),
        int(np.round(original_size[2] * (original_spacing[2] / out_spacing[2])))
    ]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(out_spacing)
    resample.SetSize(out_size)
    resample.SetOutputDirection(itk_image.GetDirection())
    resample.SetOutputOrigin(itk_image.GetOrigin())
    resample.SetTransform(sitk.Transform())
    resample.SetDefaultPixelValue(itk_image.GetPixelIDValue())

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)

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
def getCropParameters(scan=sitk.Image, marginsize=0):
    label_shape_filter = sitk.LabelShapeStatisticsImageFilter()
    label_shape_filter.Execute(scan)
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
    
    parameterMapRigid['AutomaticScalesEstimation']= ['true']
    parameterMapRigid['AutomaticTransformInitialization']= ['true']
    parameterMapRigid['AutomaticTransformInitializationMethod']= ['GeometricalCenter']
    parameterMapRigid['DefaultPixelValue']= ['0.0']
    parameterMapRigid['FinalGridSpacingInVoxels']= ['10']
    parameterMapRigid['FixedImagePyramid']= ['FixedSmoothingImagePyramid']
    parameterMapRigid['HowToCombineTransforms']= ['Compose']
    parameterMapRigid['ImageSampler']= ['Random']
    parameterMapRigid['Interpolator']= ['BSplineInterpolator']
    parameterMapRigid['MaximumNumberOfIterations']= ['2000']
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

#this is a 3D binary image filter that you can use to expand a mask in 3D
dilate_filter = sitk.BinaryDilateImageFilter()
dilate_filter.SetKernelType(sitk.sitkBall)
dilate_filter.SetKernelRadius((10,10,5))
dilate_filter.SetForegroundValue(1)

os.chdir("D:\\GBM")
basepath = os.path.join("nii_prepared")

patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
logfilepath = os.path.join(basepath, 'log_MR_to_CT.txt')
for patient in patientfolders:
    patientid = os.path.basename(patient)
    outfolder = os.path.join(patient, 'MR_to_CT')
    if not os.path.isdir(outfolder):
        os.makedirs(outfolder) 
    # create folder to save cropped images
    cropfilepath = os.path.join(patient, 'CroppedImages_MR_to_CT')
    if not os.path.isdir(cropfilepath):
        os.makedirs(cropfilepath)

    f = open(logfilepath, 'a+')

    #loop over all the files in the patient folder
    filelist = [ f.path for f in os.scandir(patient) if f.is_file() ]

    #we expect to find one CT file, one brain file, and multiple mr files
    ct_file = ''
    brain_file = ''
    mrlist = []
    for pathstr in filelist:
        if os.path.basename(pathstr).endswith('CT_res.nii.gz'):
            ct_file = pathstr
        if os.path.basename(pathstr).endswith('CT_brain.nii.gz'):
            brain_file = pathstr
        if os.path.basename(pathstr).endswith('MR_res.nii.gz'):
            mrlist.append(pathstr)

    #if there is no brainfile available, skip the patient, as we need it to do the scull stripping
    if brain_file == '':
        println = patientid + '\t' + 'no brain delineation'+ '\n'
        f.write(println)  
        f.close  
        continue

    # this is just to see the progress
    print('ctfile = ', ct_file)
    print('brainfile = ', brain_file)
    print(mrlist)
  
    #make the registration parameter map
    parameterMapRigid= rigidParameterMap()

    #The ct files are already resampled on a 1x1x1 mm grid, but the brain mask is not yet
    #the following 4 lines can be used to slice the mask to the CT grid
    ct = sitk.ReadImage(ct_file) 
    maskfilename = brain_file
    brainmask = sitk.ReadImage(maskfilename)
    brainmask = reslice_image(brainmask, ct,True)

    #We use the brainmask plus a margin of 20 mm around to evaluate the registrations later
    #so here we do the dilation of the mask
    brainmask = dilate_filter.Execute(brainmask)
    
    for mr in mrlist:
        #we make sure that all images are of datatype Float32
        moving = sitk.Cast(sitk.ReadImage(mr),sitk.sitkFloat32)
        movingfilename = os.path.basename(mr)

        regfolder = outfolder 

        #some of the rigid parametermap parameters might change, so we need to make sure these are set to the start settings  
        parameterMapRigid['AutomaticTransformInitialization']= ['true']
        parameterMapRigid['AutomaticTransformInitializationMethod']= ['GeometricalCenter']
        parameterMapRigid['NumberOfResolutions']= ['3']
        parameterMapRigid['ImagePyramidSchedule']= ['16','16','16','8','8','8', '4','4','4']
        
        #you can write the parameters for file for reading
        # sitk.WriteParameterFile(parameterMapRigid, os.path.join(regfolder, 'rigid_params.txt'))
        
        elastix = sitk.ElastixImageFilter()
        elastix.SetFixedImage(ct)
        elastix.SetMovingImage(moving)
        
        # elastix.LogToFileOn()
        elastix.SetOutputDirectory(regfolder)
        elastix.SetParameterMap(parameterMapRigid)

        #the output of elastix is the registered moving image in the grid of the CT
        MRImage = elastix.Execute()
        transf0 = elastix.GetTransformParameterMap() 
        outfilename = movingfilename
        sitk.WriteImage(MRImage, os.path.join(outfolder, outfilename))

        #the transform contains the actual registration parameters
        Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
        #this part is used to save the transform, if we want to use it later
        pre, ext = os.path.splitext(outfilename)
        transformstring1 = os.path.join(outfolder, pre + '_TranformRigid1.txt')
        if os.path.exists(transformstring1):
            os.remove(transformstring1)
        os.rename(Transform, transformstring1)
        
        #now we want to calculate the registration metric to see if the registration worked
        #for that we need to remove as much background as possible
        CTcrop = sitk.Cast(ct,sitk.sitkInt16) * sitk.Cast(brainmask,sitk.sitkInt16)
        MRImagecrop =sitk.Cast(MRImage,sitk.sitkFloat32) * sitk.Cast(brainmask,sitk.sitkFloat32)

        crop = getCropParameters(CTcrop, marginsize=0)
        croppedmoving = MRImagecrop[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
        croppedfixed = CTcrop[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
        score = calcMI(croppedfixed, croppedmoving)
        
        #saving the cropped image 1
        sitk.WriteImage(MRImage, os.path.join(cropfilepath, "MR1_" + outfilename))
        CTpath = os.path.join(cropfilepath, "CT1_" + os.path.basename(ct_file))
        if not os.path.isfile(CTpath):
            sitk.WriteImage(croppedfixed, CTpath)

        println = patientid + '\t' + movingfilename + '\t' + '{:.4f}'.format(score) + '\n'
        f.write(println)
        print(println)

        print('doing the registration again, using new start position')   
        
        #so now we change the parameters for the registration, to look more locally
        parameterMapRigid['AutomaticTransformInitialization']= ['false']
        parameterMapRigid['NumberOfResolutions']= ['2']
        parameterMapRigid['ImagePyramidSchedule']= ['4','4','4', '2','2','2' ]         
        elastix.SetParameterMap(parameterMapRigid)
        
        #and very important, we start where the first registration brought us.
        elastix.SetInitialTransformParameterFileName(transformstring1)
        #we now also use the brain mask as mask in the registration, to focus only on the important part of the image.
        elastix.SetFixedMask(brainmask)
        MRImage = elastix.Execute()

        MRImagecrop =sitk.Cast(MRImage,sitk.sitkFloat32) * sitk.Cast(brainmask,sitk.sitkFloat32)
        croppedmoving = MRImagecrop[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
        croppedfixed = CTcrop[crop[0]:crop[1], crop[2]:crop[3], crop[4]:crop[5]]
        score2 = calcMI(croppedfixed, croppedmoving)
        
         #saving cropped image 2
        sitk.WriteImage(croppedmoving, os.path.join(cropfilepath, "MR2_" + outfilename))
        CTpath = os.path.join(cropfilepath, "CT2_" + os.path.basename(ct_file))
        if not os.path.isfile(CTpath):
            sitk.WriteImage(croppedfixed, CTpath)
        
        println = patientid + '\t' + movingfilename + '_2\t' + '{:.4f}'.format(score) + '\n'
        f.write(println)
        print(println)
        #if the new score is better, use this registration
        if score2 < score:
            Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
            pre, ext = os.path.splitext(outfilename)
            transformstring2 = os.path.join(outfolder, pre + '_TranformRigid2.txt')
            if os.path.exists(transformstring2):
                os.remove(transformstring2)
            os.rename(Transform, transformstring2)
            outfilename = movingfilename
            sitk.WriteImage(MRImage, os.path.join(outfolder, outfilename))

            #there is a bug in Elastix that I can't seem to solve quickly, so this is a way around
            #here i read the transformation parameters of the first and second registration, add them,
            #and store them in the first registration transform.
            transf1 = elastix.GetTransformParameterMap()
            sum = []
            for i in range(0,6):
                sum.append(str(transf0[0]["TransformParameters"][i] +transf1[0]["TransformParameters"][i])) 
            transf0[0]["TransformParameters"]=tuple(sum)
            print(transf0[0]["TransformParameters"])
            print(transf1[0]["TransformParameters"])
            print(tuple(sum)) 

        del elastix

        #now find the GTV segmentation that belongs to the MR image, and apply the best registration to it
        MR_GTV_filename=os.path.join(patient, movingfilename.replace('MR_res', 'MR_gtv'))
        print(MR_GTV_filename)
        
        #now if we have a GTV segementation available, we can move it along with the MR to the CT
        if os.path.exists(MR_GTV_filename):
            GTVmask = sitk.ReadImage(MR_GTV_filename)

            #transformix is a part of Elastix that you can use to apply registrations to scans/segmentations   
            transformix=sitk.TransformixImageFilter()
            transformix.LogToFileOn()
            transformix.SetOutputDirectory(basepath)
            transformix.SetMovingImage(GTVmask)
            transf0[0]['FinalBSplineInterpolationOrder']=['0']
            transformfilename = movingfilename.replace('MR_res.nii.gz', 'MR_transform.txt')
            sitk.WriteParameterFile(transf0[0], os.path.join(regfolder, transformfilename))
            transformix.SetTransformParameterMap(transf0[0])
            transformix.Execute()
            GTVImage = transformix.GetResultImage()
            GTVImage = sitk.Cast(GTVImage,sitk.sitkUInt8)
            GTVfilename = movingfilename.replace('MR_res', 'MR_GTV')
            sitk.WriteImage(GTVImage, os.path.join(outfolder, GTVfilename))
            print('written ', os.path.join(outfolder, GTVfilename))

    f.close()

        



# %%

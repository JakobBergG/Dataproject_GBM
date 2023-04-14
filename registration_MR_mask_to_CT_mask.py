import SimpleITK as sitk
import os
import utils


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

#this is a 3D binary image filter that you can use to expand a mr mask in 3D
dilate_filter_mr = sitk.BinaryDilateImageFilter()
dilate_filter_mr.SetKernelType(sitk.sitkBall)
dilate_filter_mr.SetKernelRadius((10,10,5))
dilate_filter_mr.SetForegroundValue(1)

#this is a 3D binary image filter that you can use to expand a ct mask in 3D
dilate_filter_ct = sitk.BinaryDilateImageFilter()
dilate_filter_ct.SetKernelType(sitk.sitkBall)
dilate_filter_ct.SetKernelRadius((5,5,5))
dilate_filter_ct.SetForegroundValue(1)



basepath = utils.get_path('path_data')

patientfolders = [ f.path for f in os.scandir(basepath) if f.is_dir() ]
logfilepath = os.path.join(basepath, 'log_MR_to_CT_mask.txt')
for patient in patientfolders:
    patientid = os.path.basename(patient)
    outfolder = os.path.join(patient, 'MR_to_CT_mask')
    gtvfolder = os.path.join(patient, 'MR_to_CT_gtv')
    if not os.path.isdir(outfolder):
        os.makedirs(outfolder) 
    if not os.path.isdir(gtvfolder):
        os.makedirs(gtvfolder) 
        
    # print to show new patient is started
    print(patientid)


    #loop over all the ct files from the nn-Unet result
    ct_mask_path = os.path.join(patient, utils.get_path('local_path_brainmasks_ct'))
    ct_mask_filelist = [ f.path for f in os.scandir(ct_mask_path) if f.is_file() ]

    #loop over all the mr files from the nn-Unet result
    mr_mask_path = os.path.join(patient, utils.get_path('local_path_brainmasks_mr'))
    mr_mask_filelist = [ f.path for f in os.scandir(mr_mask_path) if f.is_file() ]

    # loop over all oroginal scans for the patient
    image_filelist = [ f.path for f in os.scandir(patient) if f.is_file() ]
    
    #we expect to find one CT file, one brain file, and multiple mr files
    ct_file = ''
    ct_mask = ''
    mr_list = []
    mr_masks = []
    
    # define the path for the ct file and mask
    for pathstr in ct_mask_filelist:
        if os.path.basename(pathstr).endswith('mask.nii.gz'): 
            ct_mask = pathstr

    # define the path for the mr files and masks
    for pathstr in mr_mask_filelist:
        if os.path.basename(pathstr).endswith('mask_cleaned.nii.gz'): 
            mr_masks.append(pathstr)
            
    
    # define the path for the original scans
    for pathstr in image_filelist:
        if os.path.basename(pathstr).endswith('CT_res.nii.gz'):
            ct_file = pathstr
        if os.path.basename(pathstr).endswith('MR_res.nii.gz'):
            mr_list.append(pathstr)

    
    #if there is no brainfile available, skip the patient, as we need it to do the scull stripping
    if ct_file == '':
        print("no ct_file")
        continue
  
    #make the registration parameter map
    parameterMapRigid= rigidParameterMap()

    '''
    nn-Unet makes its so that the mask and ct file already are on the same grid
    '''
    #The ct files are already resampled on a 1x1x1 mm grid, but the brain mask is not yet
    #the following 4 lines can be used to slice the mask to the CT grid
    ct = sitk.ReadImage(ct_file) 
    #maskfilename = brain_file
    ct_mask = sitk.ReadImage(ct_mask)
    #brainmask = reslice_image(brainmask, ct,True)


    
    #We use the brainmask plus a margin of 20 mm around to evaluate the registrations later
    #so here we do the dilation of the mask
    ct_mask = dilate_filter_ct.Execute(ct_mask)
    
    for (mr_file, mr_mask)  in zip(mr_list, mr_masks):
        #we make sure that all images are of datatype Float32
        mr_file_name = os.path.basename(mr_file)
        mr_mask_name = os.path.basename(mr_mask)
        mr_file = sitk.Cast(sitk.ReadImage(mr_file),sitk.sitkFloat32)
        
        # We now dialte the mr mask
        mr_mask = sitk.ReadImage(mr_mask)
        mr_mask_dilated = dilate_filter_mr.Execute(mr_mask)

        #some of the rigid parametermap parameters might change, so we need to make sure these are set to the start settings  
        parameterMapRigid['AutomaticTransformInitialization']= ['true']
        parameterMapRigid['AutomaticTransformInitializationMethod']= ['GeometricalCenter']
        parameterMapRigid['NumberOfResolutions']= ['3']
        parameterMapRigid['ImagePyramidSchedule']= ['8','8','8', '4','4','4', '2','2','2' ] 
        
        #you can write the parameters for file for reading
        # sitk.WriteParameterFile(parameterMapRigid, os.path.join(regfolder, 'rigid_params.txt'))
        
        elastix = sitk.ElastixImageFilter()
        elastix.SetFixedImage(ct)
        elastix.SetFixedMask(ct_mask)
        elastix.SetMovingImage(mr_file)
        elastix.SetMovingMask(mr_mask_dilated)
        
        # elastix.LogToFileOn()
        elastix.SetOutputDirectory(outfolder)
        elastix.SetParameterMap(parameterMapRigid)

        #the output of elastix is the registered moving image in the grid of the CT
        mr_moved = elastix.Execute()
        transf0 = elastix.GetTransformParameterMap() 
        sitk.WriteImage(mr_moved, os.path.join(outfolder, mr_file_name))
         
        del elastix


        # we want to move the mask to the ct, here we use transformix
        # transformix is a part of Elastix that you can use to apply registrations to scans/segmentations   
        transformix=sitk.TransformixImageFilter()
        transformix.LogToFileOn()
        transformix.SetOutputDirectory(outfolder)
        transformix.SetMovingImage(mr_mask)
        transf0[0]['FinalBSplineInterpolationOrder']=['0']
        transformix.SetTransformParameterMap(transf0[0])
        transformix.Execute()
        mr_mask_moved = transformix.GetResultImage()
        mr_mask_moved = sitk.Cast(mr_mask_moved,sitk.sitkUInt8)
        sitk.WriteImage(mr_mask_moved, os.path.join(outfolder, mr_mask_name.replace("mask_cleaned", "mask")))

    
    # finde the folder with the gtvs from nn-Unet for the patient and loop over all the gtvs
    patient_gtv_folder = os.path.join(patient, utils.get_path('local_path_output_gtvs'))
    patient_gtvs = [ f.path for f in os.scandir(patient_gtv_folder) if f.is_file() ]     
    
    for gtv_file_name in patient_gtvs:
        
        #now if we have a GTV segementation available, we can move it along with the MR to the CT
        if os.path.exists(gtv_file_name) and gtv_file_name.endswith('gtv.nii.gz'):
            gtv_image = sitk.ReadImage(gtv_file_name)

            #transformix is a part of Elastix that you can use to apply registrations to scans/segmentations   
            transformix=sitk.TransformixImageFilter()
            transformix.LogToFileOn()
            transformix.SetOutputDirectory(gtvfolder)
            transformix.SetMovingImage(gtv_image)
            transf0[0]['FinalBSplineInterpolationOrder']=['0']
            transformix.SetTransformParameterMap(transf0[0])
            transformix.Execute()
            gtv_moved = transformix.GetResultImage()
            gtv_moved = sitk.Cast(gtv_moved,sitk.sitkUInt8)
            sitk.WriteImage(gtv_moved, os.path.join(gtvfolder, gtv_file_name))
            
            
print('registration done')

        

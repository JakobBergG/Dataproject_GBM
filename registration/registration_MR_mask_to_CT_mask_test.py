import SimpleITK as sitk
import os
import common.utils as utils
import logging

log = logging.getLogger(__name__)

#---------------------------------------------------------#
# Elastix parameter map for rigid registration is defined #
#---------------------------------------------------------#

def rigidParameterMap():
    parameterMapRigid = sitk.GetDefaultParameterMap('rigid')
    
    parameterMapRigid['CheckNumberOfSamples']= ['false']
    parameterMapRigid['FixedImageDimension'] = ['3']
    parameterMapRigid['MovingImageDimension'] = ['3']
    parameterMapRigid['FixedInternalImagePixelType'] = ['float']
    parameterMapRigid['MovingInternalImagePixelType'] = ['float']
    
    parameterMapRigid['AutomaticScalesEstimation']= ['false']
    parameterMapRigid['Scales']= ['1000.0']
    parameterMapRigid['AutomaticTransformInitialization']= ['true']
    parameterMapRigid['AutomaticTransformInitializationMethod']= ['CenterOfGravity']
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
    parameterMapRigid['Optimizer']= ['AdaptiveStocohasticGradientDescent']
    parameterMapRigid['Registration']= ['MultiResolutionRegistration']
    parameterMapRigid['ResampleInterpolator']= ['FinalBSplineInterpolator']
    parameterMapRigid['Resampler']= ['DefaultResampler']
    parameterMapRigid['ResultImageFormat']= ['nii']
    parameterMapRigid['ResultImagePixelType']= ['unsigned short']
    parameterMapRigid['UseDirectionCosines']= ['true']
    parameterMapRigid['WriteResultImage']= ['true']    
    
    parameterMapRigid['ErodeMovingMask'] = ['false']
    parameterMapRigid['ErodeFixedMask'] = ['false']
    return parameterMapRigid

#------------------------------#
# Dilation filters are defined #
#------------------------------#

# create 3D binary image filter used to expand the mr masks 5 mm in 3D
dilate_filter_mr = sitk.BinaryDilateImageFilter()
dilate_filter_mr.SetKernelType(sitk.sitkBall)
dilate_filter_mr.SetKernelRadius(utils.get_setting("registration_dilation_radius_mr")) 
dilate_filter_mr.SetForegroundValue(1)

# create 3D binary image filter used to expand the mr masks 5 mm in 3D
dilate_filter_ct = sitk.BinaryDilateImageFilter()
dilate_filter_ct.SetKernelType(sitk.sitkBall)
dilate_filter_ct.SetKernelRadius(utils.get_setting("registration_dilation_radius_ct"))
dilate_filter_ct.SetForegroundValue(1)


def register_MR_to_CT(patient_folder : str):
    patient_id = os.path.basename(patient_folder)
    outfolder = os.path.join(patient_folder, utils.get_path('local_path_moved_mr')) 
    gtvfolder = os.path.join(patient_folder, utils.get_path('local_path_moved_gtv')) 
    if not os.path.isdir(outfolder):
        os.makedirs(outfolder) 
    if not os.path.isdir(gtvfolder):
        os.makedirs(gtvfolder) 
        
    # log start of new patient
    log.info(f"Starting registration for patient {patient_id}")
    
    # set the registration parameter map as defined above
    parameterMapRigid = rigidParameterMap()

    #------------------------------------------------------------#
    # Find the PathString of the different scans for the patient #
    #------------------------------------------------------------#

    # loop over all the files in the nn-Unet output folder for CT brain segmentation 
    ct_mask_path = os.path.join(patient_folder, utils.get_path('local_path_brainmasks_ct'))
    ct_mask_filelist = [ f.path for f in os.scandir(ct_mask_path) if f.is_file() ]

    # loop over all the files in the nn-Unet output folder for MR brain segmentation 
    mr_mask_path = os.path.join(patient_folder, utils.get_path('local_path_brainmasks_mr'))
    mr_mask_filelist = [ f.path for f in os.scandir(mr_mask_path) if f.is_file() ]

    # loop over all original scans for the patient
    image_filelist = [ f.path for f in os.scandir(patient_folder) if f.is_file() ]

    # find all GTVs for the patient
    patient_gtv_folder = os.path.join(patient_folder, utils.get_path('local_path_gtv'))
    patient_gtvs = [ f.path for f in os.scandir(patient_gtv_folder) if f.is_file() ] 
    
    # we expect to find one CT file, with corrosponding mask, for each patient
    ct_file = ''
    ct_mask = ''
    
    # we expect to find multiple MR files, each with corrosponding mask, for each patient
    mr_list = []
    mr_masks = []
    
    # we expect to find multiple GTVs for each patient
    gtv_list = []
    
    # define the path for the ct file and mask
    for pathstr in ct_mask_filelist:
        if os.path.basename(pathstr).endswith('mask_cleaned.nii.gz'): 
            ct_mask = pathstr

    # define the path for the mr files and masks
    for pathstr in mr_mask_filelist:
        if os.path.basename(pathstr).endswith('mask_cleaned.nii.gz'): 
            mr_masks.append(pathstr)

    # define the path for the gtv segmentations
    for pathstr in patient_gtvs:
        if os.path.basename(pathstr).endswith('gtv.nii.gz'): 
            gtv_list.append(pathstr)
            
    
    # define the path for the original scans
    for pathstr in image_filelist:
        if os.path.basename(pathstr).endswith('CT_res.nii.gz'):
            ct_file = pathstr
        if os.path.basename(pathstr).endswith('MR_res.nii.gz'):
            mr_list.append(pathstr)

    
    # if there is no brainfile available, raise exception
    if ct_file == '':
        log.error(f"No CT file for patient {patient_id}")
        raise Exception(f"No CT file for patient {patient_id}")

    #----------------------------------------#
    # Read and update the different CT files #
    #----------------------------------------#
    
    # reading the CT scan and CT mask
    ct_image = sitk.ReadImage(ct_file) 
    ct_mask = sitk.ReadImage(ct_mask)

    
    # set the direction cosines for the mask and scan to be equal
    ct_mask.CopyInformation(ct_image)
    
    # strip CT image based on CT mask for first round of registration
    ct_stripped = sitk.Mask(ct_image,ct_mask)

    
    # we use the brainmask plus a margin of 20 mm around in the second round of registration
    ct_mask_dilated = dilate_filter_ct.Execute(ct_mask)
    
    for (mr_file, mr_mask, gtv_file)  in zip(mr_list, mr_masks, gtv_list):
     
        #------------------------------------------------#
        # Read and update the different MR and GTV files #
        #------------------------------------------------#
        
        # define path to the MR scan and MR mask
        mr_file_name = os.path.basename(mr_file)
        mr_mask_name = os.path.basename(mr_mask)
        
        # reading the MR scan and MR mask
        mr_image = sitk.Cast(sitk.ReadImage(mr_file),sitk.sitkFloat32)
        mr_mask = sitk.ReadImage(mr_mask)
        
        # reading the corrosponding GTV
        gtv_file_name = os.path.basename(gtv_file)
        
        # make sure that the mask and image have same direction cosines
        mr_mask.CopyInformation(mr_image)
        
        # strip MR image based on MR mask for first round of registration
        mr_stripped = sitk.Mask(mr_image,mr_mask)
        
        # we use the brainmask plus a margin of 20 mm around in the second round of registration
        mr_mask_dilated = dilate_filter_mr.Execute(mr_mask)

        #-----------------------------#
        # First round of registration #
        #-----------------------------#
        
        # define specific parametermap for first round of registration
        parameterMapRigid['AutomaticTransformInitialization']= ['true']
        parameterMapRigid['AutomaticTransformInitializationMethod']= ['CenterOfGravity']
        parameterMapRigid['NumberOfResolutions']= ['1']
        parameterMapRigid['ImagePyramidSchedule']= ['8','8','8']
        
        # defining the images used in the first round of registration
        # we use skull-stripped versions of the scans in the first round
        elastix = sitk.ElastixImageFilter()
        elastix.SetFixedImage(ct_stripped)
        elastix.SetMovingImage(mr_stripped)
        
        # activate log file and define output folder and parameters.
        elastix.LogToFileOn()
        elastix.SetOutputDirectory(outfolder)
        elastix.SetParameterMap(parameterMapRigid)

        # execute Elastix and save the paramtermap used by Elastix
        elastix.Execute()
        transf0 = elastix.GetTransformParameterMap() 
        
        # change the name of the log file from Elastix 
        # this file contains information about the above executed transformation
        Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
        pre, ext = os.path.splitext(mr_file_name)
        transformstring = os.path.join(outfolder, pre + '_TranformRigid1.txt')
        if os.path.exists(transformstring):
            os.remove(transformstring)
        os.rename(Transform, transformstring)
        
        #------------------------------#
        # Second round of registration #
        #------------------------------#
        
        # define specific parametermap for first second of registration
        parameterMapRigid['AutomaticTransformInitialization']= ['false']
        parameterMapRigid['NumberOfResolutions']= ['3']
        parameterMapRigid['ImagePyramidSchedule']= ['8','8','8', '4','4','4', '2','2','2' ]         
        elastix.SetParameterMap(parameterMapRigid)
        
        # start the second round where the first round ended.
        elastix.SetInitialTransformParameterFileName(transformstring)
        
        # define the images used in the second round of registration
        # we use the entire scans in the second round
        elastix.SetFixedImage(ct_image)
        elastix.SetMovingImage(mr_image)
        
        # in this round we also use a moving and fixed mask.
        elastix.SetFixedMask(ct_mask_dilated)
        elastix.SetMovingMask(mr_mask_dilated)
        
        # execute Elastix and save the moved MR file and the paramtermap used by Elastix
        mr_moved = elastix.Execute()
        transf1 = elastix.GetTransformParameterMap()
        
        # change the name of the log file from Elastix 
        # this file contains information about the above executed transformation
        Transform = os.path.join(outfolder, 'TransformParameters.0.txt')
        pre, ext = os.path.splitext(mr_file_name)
        transformstring = os.path.join(outfolder, pre + '_TranformRigid2.txt')
        if os.path.exists(transformstring):
            os.remove(transformstring)
        os.rename(Transform, transformstring)
        
        #-----------------------------#
        # Save result of registration #
        #-----------------------------#
        
        # sum the parametermaps from the two rounds of registrations into one map.
        parameters_sum = []
        for i in range(0,6):
            parameters_sum.append(str(transf0[0]["TransformParameters"][i] +transf1[0]["TransformParameters"][i])) 
        transf0[0]["TransformParameters"]=tuple(parameters_sum)
        
        # write the moved mr image
        sitk.WriteImage(mr_moved, os.path.join(outfolder, mr_file_name))
        
        del elastix

        #------------------------------------------------------------#
        # Move MR mask to CT based on the result of the registration #
        #------------------------------------------------------------#

        # we want to move the MR mask to the CT scan, to do so we use transformix.
        # we use the summed parameter map to move the mask in the same direction as the MR
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

        #--------------------------------------------------------#
        # Move GTV to CT based on the result of the registration #
        #--------------------------------------------------------#

        # read the GTV corrosponding to the above moved MR
        gtv_image = sitk.ReadImage(gtv_file)

        # we want to move the GTV to the CT scan, to do so we use transformix.
        # we use the summed parameter map to move the GTV in the same direction as the MR 
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
        
        log.info(f"Done with registration for patient {patient_id}")
            

        

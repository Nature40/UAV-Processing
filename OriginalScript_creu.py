﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
# script version 0.2.1
"""
© Copyright 2017, Chris Reudenbach, Sebastian Richter
update 2019 06 13 Chris Reudenbach
basicPSWorkflow.py: 


the first three most commonly used are:
goal = ["singleOrtho","allOrtho","singleDense","allDense","filter"]
imgPath = "path_to_the_image_data"
projName "name_of_the_project_file.psx"

xOrtho: performs a workflow for a standarized generation of ortho images 
based on low altitude uav imagery over rugged surfaces. it adds
images to a new chunk, align them and optimized iteratively by 
filtering the resulting sparse point cloud. The ortho image is build by  
constructing first a smoothed mesh model and second a DSM. 

xDense: performs a workflow for a standarized generation of a dense point 
cloud based on low altitude uav imagery over rugged surfaces. It adds
images to a new chunk, align them and optimized iteratively by 
filtering the resulting sparse point cloud. The dense point cloud is 
is build upon this optimized sparse cloud. 

filter: performs a workflow for a standarized filter procedure for all 
chunks that have to contain a sparse point cloud. They will be optimized
iteratively. 

In the end of all workflows an automated report is generated.
Full documentation is provided at https://github.com/gisma/uavRmp
"""

# It can be run directly in Photoscan or can be added to a batch process.

# NOTE: Preset values are choosen to fit most picture settings but might have to be adjusted for specific situations.

### Used references:
# http://www.agisoft.com/forum/index.php?topic=5536.0
# http://www.agisoft.com/pdf/photoscan_python_api_1_3_2.pdf
# http://www.agisoft.com/forum/index.php?topic=3164.0
# http://www.agisoft.com/forum/index.php?topic=2767.0
# http://www.agisoft.com/forum/index.php?topic=5976.315 
# http://www.agisoft.com/forum/index.php?topic=2236.0
# http://www.agisoft.com/forum/index.php?topic=6287.msg30374#msg30374
# http://www.agisoft.com/forum/index.php?topic=1981.0
# http://www.agisoft.com/forum/index.php?topic=1843.0
# http://www.agisoft.com/forum/index.php?topic=1881.0
# https://github.com/dshean/sfm_tools/blob/master/agisoft_all.py
# http://www.agisoft.com/pdf/photoscan-pro_1_3_en.pdf
# http://www.agisoft.com/pdf/photoscan_python_api_1_3_2.pdf   <- Using Python in Photoscan
# https://dinosaurpalaeo.wordpress.com/2015/10/11/photogrammetry-tutorial-11-how-to-handle-a-project-in-agisoft-photoscan/ <- general information for the interaction between the three used values
# http://www.agisoft.com/forum/index.php?topic=738.0  <- Reprojection Error
# http://www.agisoft.com/forum/index.php?topic=2478.0  <- Reconstruction Uncertainty, Photoscan users explaining how they tested/experimented with values and giving advises in which range the single parameters give reasonable results


# https://www.agisoft.com/forum/index.php?topic=9567.0 <- depth map filtering


import Metashape
import os
import sys
import re
import glob
from os.path import expanduser


# preset parameters
goal = "allOrtho"          # script mode							sys.argv[1]
imgPath = "X:/nature40/pheno_processing/exports_new"       # path to images PATH TO EXPORT TIFs 							sys.argv[2]
projName = "phenoDates2.psx"      # project name with suffix ".psx"		sys.argv[3]
alignQuality = 2  # alignment quality						sys.argv[4]
orthoRes = 0.05      # resolution of the ortho image pixels	sys.argv[5]
refPre = Metashape.ReferencePreselection #Metashape.GenericPreselection        # reference preselection mode			sys.argv[6]
preset_RU = 50     # reconstruction  uncertainty threshold	sys.argv[7]
preset_RE = 1     # Reprojection error threshold			sys.argv[8]
preset_PA = 10     # Projection Accuracy treshold			sys.argv[9]
loop_RU = 3       # loops reconstruction uncertainty		sys.argv[10]
loop_RE = 4       # loops reprojection error				sys.argv[11]
loop_PA = 2       # loops projection accuray				sys.argv[12]
filter_mode = Metashape.ModerateFiltering   # Metashape filtermode for dense cloud 	sys.argv[13]
dc_quality = Metashape.LowQuality    # desne cloud quality 					sys.argv[14]
passes = 25        # number of mesh grid smoothing passes	sys.argv[15]
tpl = 4000
kpl = 40000
crs = Metashape.CoordinateSystem("EPSG::25832")

print("The script is running")
# activate document         
crs1 =  Metashape.CoordinateSystem("EPSG::25832")
doc = Metashape.app.document
doc.read_only = False
print("current document is: ",  doc)
#chunk = doc.addChunk()
chunk = doc.chunks
print("current chunk is: ",  chunk)
PSPCF = Metashape.PointCloud.Filter()


path = Metashape.app.getSaveFileName("Save Project As")
try:
	doc.save(path)
except RuntimeError:
	Metashape.app.messageBox("Can't save project")

#Metashape.app.messageBox("You are running the script:" + sys.argv[0] + "\n\n" +
#						"Mode:                       " + goal +"\n" +
#						"Image Path:                 " + imgPath + "\n" +
#						"Project Name:               " + projName +"\n\n")
						

def filterSparse(doc,chunk,PSPCF,goal):
	
#### Definitions taken from the Agisoft Metashape Manual, Professional Edition (version 1.3)
### Reprojection error
# High  reprojection  error  usually  indicates  poor  localization  accuracy  of  the  corresponding  point
# projections at the point matching step. It is also typical for false matches. Removing such points can
# improve accuracy of the subsequent optimization step.

### High  reconstruction  uncertainty  is  typical  for  points,  reconstructed  from  nearby  photos  with  small
# baseline. Such points can noticeably deviate from the object surface, introducing noise in the point
# cloud. While removal of such points should not affect the accuracy of optimization, it may be useful
# to remove them before building geometry in Point Cloud mode or for better visual appearance of the
# point cloud.

### Image count (not used so far)
# Metashape reconstruct all the points that are visible at least on two photos. However, points that are
# visible only on two photos are likely to be located with poor accuracy. Image count filtering enables
# to remove such unreliable points from the cloud.
 
### Projection Accuracy
# This criterion allows to filter out points which projections were relatively poorer localised due to their
# bigger size.
 
### Calibration parameters list:
# f = Focal length measured in pixels.
# cx, cy = Principal point coordinates, i.e. coordinates of lens optical axis interception with sensor plane in pixels.
# b1, b2 = Affinity and Skew (non-orthogonality) transformation coefficients.
# k1, k2, k3, k4 = Radial distortion coefficients.
# p1, p2, p3, p4 = Tangential distortion coefficients.
	
	count = 0
	cl = doc.chunks		# list of all chunks of a document
	
	# get an overview of the chunks and if they are already aligned
	#print(cl)
	#print(len(cl))
	
	for chunk in doc.chunks:
		noPoints = False
		print("Chunk")
		#print("chunk " + str(chunk))
		pc = chunk.point_cloud
		#print("point cloud number" + str(pc))
		m = re.search('PointCloud', str(pc))
		if m:
			noPoints = True
		else:
			noPoints = False
		
		#print("noPoints = " + str(noPoints))
		
		if (noPoints == False  and goal == "filter"):
			### align photos
			#   matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=0, tiepoint_limit=0[, progress])
			#   Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy] ranging from [0-5]
			#   Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
			#print("matching Photos of chunk" + str(chunk))
			chunk.matchPhotos(accuracy=alignQuality, preselection=refPre, keypoint_limit=kpl, tiepoint_limit=tpl)
			#print("aligning cameras...")
			chunk.alignCameras()
			
			
			chunk.exportPoints(str(imgPath + "/" + str(chunk.label) + "_original.las"), source = Metashape.DataSource.PointCloudData, colors = True, projection = crs)
			
			
			doc.read_only = False
			doc.save()
			ex = True
			noPoints = True
		if (noPoints):
			# optimize Point Cloud by setting ReconstructionUncertainty
			# Technical NOTE: the process runs several times as the optimizing of the camera results in points that have higher values again than the threshold value
			#                 that was used before to limit the Reconstruction Uncertainty. It was found that the more often this process runs the less points will 
			#                 be deleted in each step so that finally the point cloud has the choosen Reconstruction Uncertainty 
			#                 and keeps it after the cameras are optimized
			while count < loop_RU:
				print("filtering RU " )
				class ReconstructionUncertainty:
					# select points by Reconstruction Uncertainty
					PSPCF.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)		
					PSPCF.selectPoints(preset_RU)
					# remove points
					if hasattr(chunk, 'removeSelectedPoints'):
						chunk.point_cloud.removeSelectedPoints()
						# optimize cameras			
						chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
						chunk.resetRegion()
				
				count=count+1  
				continue
			
			count = 0

			# optimize Point Cloud by setting ReprojectionError
			# See technical NOTE for Reconstruction Uncertainty why to repeat this process several times
			while count < loop_RE:
				class ReprojectionError:
					# select points by Reprojection Error
					PSPCF.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)		
					PSPCF.selectPoints(preset_RE)
					if hasattr(chunk, 'removeSelectedPoints'):
						chunk.point_cloud.removeSelectedPoints()
						# optimize cameras			
						chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
						chunk.resetRegion()
				count=count+1  
				continue
			
			count = 0
			
			# optimize Point Cloud by setting ProjectionAccuracy
			# [TODO: No improve in the second run?? Then set runs to 1, or remove loop]
			while count< loop_PA:
				class ProjectionAccuracy:
					# select points by Projection Accuracy
					PSPCF.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)		
					PSPCF.selectPoints(preset_PA)
					if hasattr(chunk, 'removeSelectedPoints'):
						chunk.point_cloud.removeSelectedPoints()
						# optimize cameras			
						chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
						chunk.resetRegion()
				count=count+1  
				continue
			count = 0
			doc.read_only = False
			doc.save()
        	
        	### create Processing Report path 
			if goal == "filter":
				file_path = doc.path
				file_path_cut = file_path[0:-4]		
				report_path = (file_path_cut + "_reports")
				if not os.path.exists(report_path):
					os.makedirs(report_path)

				### export Processing Report
				chunk.exportPoints(str(imgPath + "/" + str(chunk.label) + "_filtered.las"), source = Metashape.DataSource.PointCloudData, colors = True, projection = crs)
				chunk.exportReport(report_path + "/" + chunk.label + ".pdf")
				#print("sparse point clouds optimized by setting:\n Reconstruction Uncertainty = " + "{:.0f}".format(preset_RU) + " >> " + "{:.0f}".format(loop_RU) + " loop(s)\n"+
			    #                                      "         Reprojection Error = " + "{:.0f}".format(preset_RE) + " >> " + "{:.0f}".format(loop_RE) + " loop(s)\n"+ 
			    #                                      "        Projection Accuracy = " + "{:.0f}".format(preset_PA) + " >> " + "{:.0f}".format(loop_PA) + " loop(s)\n")	
				#print("Processing Reports were created and saved to " +report_path)


def makemesh(doc,chunk,PSPCF):
	### GENERATE MESH 
	#   buildModel(surface=Arbitrary, interpolation=EnabledInterpolation, face_count=MediumFaceCount[, source ][, classes][, progress])
	#   Surface type in [Arbitrary, HeightField]
	#   Interpolation mode in [EnabledInterpolation, DisabledInterpolation, Extrapolated]
	#   Face count in [HighFaceCount, MediumFaceCount, LowFaceCount]
	#   Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
	chunk.buildModel(surface=Metashape.SurfaceType.HeightField, source = Metashape.DataSource.PointCloudData, interpolation = Metashape.Interpolation.EnabledInterpolation, face_count = Metashape.FaceCount.MediumFaceCount)
	chunk.smoothModel(passes)				
	# save project before buildDem and buildOrthomosaic is called
	doc.save()
	

### ortho creates an standarized optimized ortho image from uav imagery  
#   you can call it with singleOrtho and allOrtho argument
def ortho(doc,chunk,PSPCF,goal):
	cl = doc.chunks		# list of all chunks of a document
	
	# get an overview of the chunks and if they are already aligned
	#print(cl)
	#print(len(cl))
	ex = False
	
	### if all chunks are requested to be processed
	if goal == "allOrtho":			
		print("Im in the allOrtho function")
		for chunk in doc.chunks:
			noPoints = False
			#print(chunk)
			pc = chunk.point_cloud
			print((str(imgPath + "/" + str(chunk.label))))
			
			m = re.search('PointCloud', str(pc))
			if m:
				noPoints = True
			else:
				noPoints = False
			
			print("noPoints Check = ",  noPoints)
	
			if (noPoints == False):    
				### call filter sequence
				print("filter ")
				filterSparse(doc,chunk,PSPCF,"filter")
			
				### GENERATE MESH 
				#   buildModel(surface=Arbitrary, interpolation=EnabledInterpolation, face_count=MediumFaceCount[, source ][, classes][, progress])
				#   Surface type in [Arbitrary, HeightField]
				#   Interpolation mode in [EnabledInterpolation, DisabledInterpolation, Extrapolated]
				#   Face count in [HighFaceCount, MediumFaceCount, LowFaceCount]
				#   Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
				#print ()
				chunk.buildModel(surface=Metashape.SurfaceType.HeightField, source = Metashape.DataSource.PointCloudData, interpolation = Metashape.Interpolation.EnabledInterpolation, face_count = Metashape.FaceCount.LowFaceCount)
				chunk.smoothModel(passes)				
				# save project before buildDem and buildOrthomosaic is called
				doc.save()
				
				### GENERATE DEM
				#   Build elevation model for the chunk.
				#   buildDem(source=DenseCloudData, interpolation=EnabledInterpolation[, projection ][, region ][, classes][, progress])
				#   Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
				##chunk.buildDem(source = Metashape.DataSource.ModelData, interpolation=Metashape.EnabledInterpolation,dx=orthoRes*20,dy=orthoRes*20)
				##doc.save()
					
				### GENERATE ORTHOMOSAIC
				#   buildOrthomosaic(surface=ElevationData, blending=MosaicBlending, color_correction=False[, projection ][, region ][, dx ][, dy ][, progress])
				#   Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
				#   Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
				chunk.buildOrthomosaic(surface=Metashape.ModelData,projection=crs,dx=orthoRes,dy=orthoRes)
				doc.save()
				
				chunk.exportOrthomosaic(str(imgPath + "/" + str(chunk.label) + ".tif"), projection=crs, raster_transform=Metashape.RasterTransformNone,
				write_kml=True, write_world=True, write_alpha=True, tiff_big=True, tiff_compression=Metashape.TiffCompressionNone, white_background=True,dx=orthoRes,dy=orthoRes)

			
				### create Processing Report path 
				file_path = doc.path
				file_path_cut = file_path[0:-4]		
				report_path = (file_path_cut + "_reports")
				if not os.path.exists(report_path):
					os.makedirs(report_path)
						
				### export Processing Report
				chunk.exportReport(report_path + "/" + chunk.label + ".pdf")
				
				### #print some information	
				#print("sparse point clouds optimized by setting:\n Reconstruction Uncertainty = " + "{:.0f}".format(preset_RU) + " >> " + "{:.0f}".format(loop_RU) + " loop(s)\n"+
			    #                                      "         Reprojection Error = " + "{:.0f}".format(preset_RE) + " >> " + "{:.0f}".format(loop_RE) + " loop(s)\n"+ 
			    #                                      "        Projection Accuracy = " + "{:.0f}".format(preset_PA) + " >> " + "{:.0f}".format(loop_PA) + " loop(s)\n")	
				#print("Processing Reports were created and saved to " + report_path)
				# define general short variables
				count = 0
				if (ex):
					break
			else:
				print("Making a mesh")
				### GENERATE MESH 
				#   buildModel(surface=Arbitrary, interpolation=EnabledInterpolation, face_count=MediumFaceCount[, source ][, classes][, progress])
				#   Surface type in [Arbitrary, HeightField]
				#   Interpolation mode in [EnabledInterpolation, DisabledInterpolation, Extrapolated]
				#   Face count in [HighFaceCount, MediumFaceCount, LowFaceCount]
				#   Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
				#print ()
				chunk.buildModel(surface=Metashape.SurfaceType.HeightField, source = Metashape.DataSource.PointCloudData, interpolation = Metashape.Interpolation.EnabledInterpolation, face_count = Metashape.FaceCount.LowFaceCount)
				chunk.smoothModel(passes)				
				# save project before buildDem and buildOrthomosaic is called
				doc.save()
				
				### GERNERATE ORTHO
				chunk.buildOrthomosaic(surface=Metashape.ModelData,projection=crs,dx=orthoRes,dy=orthoRes)
				doc.save()
				
				chunk.exportOrthomosaic(str(imgPath + "/" + str(chunk.label) + ".tif"), projection=crs, raster_transform=Metashape.RasterTransformNone,
				write_kml=True, write_world=True, write_alpha=True, tiff_big=True, tiff_compression=Metashape.TiffCompressionNone, white_background=True,dx=orthoRes,dy=orthoRes)
				### create Processing Report path 
				file_path = doc.path
				file_path_cut = file_path[0:-4]		
				report_path = (file_path_cut + "_reports")
				if not os.path.exists(report_path):
					os.makedirs(report_path)
						
				### export Processing Report
				chunk.exportReport(report_path + "/" + chunk.label + ".pdf")
				count = 0
				if (ex):
					break
				
### ortho creates an standarized optimized dense point cloud from uav imagery  
#   you can call it with singleDense and allDense argument
def dense(doc,chunk,PSPCF,goal):
	cl = doc.chunks		# list of all chunks of a document
	
	# get an overview of the chunks and if they are already aligned
	#print(cl)
	#print(len(cl))
	ex = False
	
	### if just one chunk is requested to be processed
	if goal == "singleDense":			
		# creating image list
		#image_list = glob.glob(imgPath + "/*.JPG")
		##print(image_list)
		# load images
		#chunk.addPhotos(image_list)
		# load exif data
		chunk.loadReferenceExif()
		# create project
		doc.save(imgPath + "/" + projName)
		# reopen it
		doc.open(imgPath + "/" + projName)
		chunk = doc.chunk
		#print(chunk)
		### align photos
		#   matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=0, tiepoint_limit=0[, progress])
		#   Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy] ranging from [0-5]
		#   Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
		chunk.matchPhotos(accuracy=alignQuality, preselection=refPre, keypoint_limit=kpl, tiepoint_limit=tpl)
		chunk.alignCameras()
		doc.save()
		ex = True
		goal = "allDense"	
	
	### if more than one chunk is available and desired to be processed
	if goal == "allDense":			
		
		for chunk in doc.chunks:
			noPoints = False
			#print(chunk)
			pc = chunk.point_cloud
			#print(pc)
			m = re.search('PointCloud', str(pc))
			if m:
				noPoints = True
			else:
				noPoints = False
			
			#print(noPoints)
			if (noPoints == False and goal == "allDense"):
				### align photos
				#   matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=0, tiepoint_limit=0[, progress])
				#   Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy] ranging from [0-5]
				#   Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
				chunk.matchPhotos(accuracy=alignQuality, preselection=refPre, keypoint_limit=0, tiepoint_limit=0)
				chunk.alignCameras()
				doc.save()
				ex = True
				noPoints = True
	
			if (noPoints):    
			
				### call filter sequence
				filterSparse(doc,chunk,PSPCF)
			
				# save project before buildDem and buildOrthomosaic is called
				doc.save()
				### dense cloud model
				#    Generate depth maps for the chunk.
				#    buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
				#    Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
				#    Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
				chunk.buildDenseCloud(quality=dc_quality, filter=filter_mode, keep_depth=True, reuse_depth=False)
				doc.save()

				### create Processing Report path 
				file_path = doc.path
				file_path_cut = file_path[0:-4]		
				report_path = (file_path_cut + "_reports")
				if not os.path.exists(report_path):
					os.makedirs(report_path)
						
				### export Processing Report
				chunk.exportReport(report_path + "/" + chunk.label + ".pdf")
				
				### #print some information	
				#print("sparse point clouds optimized by setting:\n Reconstruction Uncertainty = " + "{:.0f}".format(preset_RU) + " >> " + "{:.0f}".format(loop_RU) + " loop(s)\n"+
			    #                                      "         Reprojection Error = " + "{:.0f}".format(preset_RE) + " >> " + "{:.0f}".format(loop_RE) + " loop(s)\n"+ 
			    #                                      "        Projection Accuracy = " + "{:.0f}".format(preset_PA) + " >> " + "{:.0f}".format(loop_PA) + " loop(s)\n")	
				#print("Processing Reports were created and saved to " + report_path)
				# define general short variables
				count = 0
				if (ex):
					break
	

### Kind of Main 

if goal == "filter":
	### call filter sequence
	filterSparse(doc,chunk,PSPCF,goal)
elif (goal == "allOrtho" or goal =="singleOrtho"):
	### call filter sequence
	ortho(doc,chunk,PSPCF,goal)
### dense creates an standarized optimized dense point cloud (depth map) from uav imagery		
elif (goal == "allDense" or goal =="singleDense"):    
	### call filter sequence
	#print("JA")
	dense(doc,chunk,PSPCF,goal)
elif (goal == "mesh"):
	makemesh(doc,chunk,PSPCF)
elif (goal == "mesh"):
	makedgm(doc,chunk,PSPCF)	

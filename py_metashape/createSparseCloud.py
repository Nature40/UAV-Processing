#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:00:09 2019

@author: marvin


"""

import Metashape
import sys

# control: do with all chunks or just the active one
allchunks = sys.argv[1]



def filterSparse(chunk, doc = Metashape.app.document, alignQuality = 2, kpl = 40000, tpl = 4000):
    
    outpath = doc.path[:-4]  # project path without file extension
    crs = Metashape.CoordinateSystem("EPSG::25832")
    
    # align photos
    chunk.matchPhotos(accuracy=alignQuality, preselection = Metashape.ReferencePreselection,
                      keypoint_limit = kpl, tiepoint_limit = tpl)
    
    chunk.alignCameras()
    chunk.resetRegion()
    
    # export original tiepoints
    
    chunk.exportPoints(str(outpath + "_" + str(chunk.label) + "_tiepoints_original.las"), source = Metashape.DataSource.PointCloudData, colors = True, projection = crs)
       
    # # # # FILTER CLOUDS # # # #
    #----------------------------------------------------
    MF = Metashape.PointCloud.Filter()
        
    # Reconstruction Accuracy Filter
    for i in range(3-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)		
        MF.selectPoints(50)
        chunk.point_cloud.removeSelectedPoints()
        chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
        chunk.resetRegion()     
    
    # Reprojection Error Filter
    for i in range(4-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)		
        MF.selectPoints(1)
        chunk.point_cloud.removeSelectedPoints()
        chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
        chunk.resetRegion()
    
    # Projection Accuracy Filter    
    for i in range(2-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)		
        MF.selectPoints(10)
        chunk.point_cloud.removeSelectedPoints()	
        chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True)
        chunk.resetRegion()
        
    #------------------------------------------------------------------------
    
    # export filtered tiepoints
    chunk.resetRegion()
    chunk.exportPoints(str(outpath + "_" + str(chunk.label) + "_tiepoints_filtered.las"), source = Metashape.DataSource.PointCloudData, colors = True, projection = crs)
        
    # save document
    doc.read_only = False
    doc.save()
    
    # create report
    chunk.exportReport(outpath + "_" + chunk.label + "_report.pdf")
    


# control: do with all chunks or just the active one
def filterSparseControl(allchunks):  
    print(allchunks)
    if allchunks == "1": 
        for i in Metashape.app.document.chunks:
            filterSparse(chunk = i)
    else:
        filterSparse(chunk = Metashape.app.document.chunk)

        
# RUN CONTROL

filterSparseControl(allchunks)



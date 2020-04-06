#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:00:09 2019

@author: marvin


"""

import Metashape


def createSparse(chunk, doc = Metashape.app.document, kpl = 40000, tpl = 4000):
    
    # align photos
    chunk.matchPhotos(downscale = 1, reference_preselection = True,
                      keypoint_limit = kpl, tiepoint_limit = tpl)
    
    chunk.alignCameras(adaptive_fitting = True)
    chunk.resetRegion()
    
    # save document
    doc.read_only = False
    doc.save()


def filterSparse(chunk, doc = Metashape.app.document):
    
    MF = Metashape.PointCloud.Filter()
    # Reconstruction Accuracy Filter
    for i in range(3-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)		
        MF.selectPoints(50)
        chunk.point_cloud.removeSelectedPoints()
        chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy = True, fit_b1=True, fit_b2 = True, fit_k1 = True, fit_k2 = True, fit_k3 = True, fit_k4=True, fit_p1 = True, fit_p2 =True)
        chunk.resetRegion()     
    
    # Reprojection Error Filter
    for i in range(4-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)		
        MF.selectPoints(1)
        chunk.point_cloud.removeSelectedPoints()
        chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy = True, fit_b1=True, fit_b2 = True, fit_k1 = True, fit_k2 = True, fit_k3 = True, fit_k4=True, fit_p1 = True, fit_p2 =True)
        chunk.resetRegion()
    
    # Projection Accuracy Filter    
    for i in range(2-1):
        MF.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)		
        MF.selectPoints(10)
        chunk.point_cloud.removeSelectedPoints()	
        chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy = True, fit_b1=True, fit_b2 = True, fit_k1 = True, fit_k2 = True, fit_k3 = True, fit_k4=True, fit_p1 = True, fit_p2 =True)
        chunk.resetRegion()
        
    #------------------------------------------------------------------------


def exportSparse(chunk, doc = Metashape.app.document):

    outpath = doc.path[:-4]  # project path without file extension
    crs = Metashape.CoordinateSystem("EPSG::25832")

    # export filtered tiepoints
    chunk.exportPoints(str(outpath + "_" + str(chunk.label) + "_tiepoints.las"), source_data = Metashape.DataSource.PointCloudData, save_colors = True, crs = crs)
        
    # save document
    doc.read_only = False
    doc.save()
    

    


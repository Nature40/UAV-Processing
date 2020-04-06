#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:47:53 2019

@author: marvin
"""

import Metashape

# control: do with all chunks or just the active one
def sparse2ortho(chunk, doc = Metashape.app.document, orthoRes = 0.05):
 
    
    # create mesh
    chunk.resetRegion()
    chunk.buildModel(surface_type=Metashape.SurfaceType.HeightField, source_data = Metashape.DataSource.PointCloudData,
                     interpolation = Metashape.Interpolation.EnabledInterpolation, face_count = Metashape.FaceCount.HighFaceCount)
    chunk.smoothModel(35)	
    doc.save()
    
    
    # build ortho
    chunk.resetRegion()
    chunk.buildOrthomosaic(surface_data=Metashape.ModelData, resolution = orthoRes)
    doc.save()
    

#def dense2ortho(chunk, doc = Metashape.app.document, orthoRes = 0.05):
    


def exportOrtho(chunk, doc = Metashape.app.document, orthoRes = 0.05):

    outpath = doc.path[:-4]  # project path without file extension
    
    # export ortho
    chunk.resetRegion()
    chunk.exportRaster(str(outpath + "_" + str(chunk.label) + "_orthomosaic.tif"),
                raster_transform = Metashape.RasterTransformNone,save_alpha=False,
                white_background=True, resolution = orthoRes, source_data = Metashape.DataSource.OrthomosaicData)
    # save document
    doc.read_only = False
    doc.save()
    # create report
    chunk.exportReport(outpath + "_" + chunk.label + "_report.pdf") 

def exportSeamlines(chunk, doc = Metashape.app.document):
    outpath = doc.path[:-4]
    chunk.buildSeamlines(epsilon = 0)
    # save document
    doc.read_only = False
    doc.save()
    chunk.exportShapes(path = str(outpath + "_" + str(chunk.label) + "_seamlines.geojson"), save_polygons = True)
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 09:47:53 2019

@author: marvin
"""

import Metashape
import sys

# control: do with all chunks or just the active one
allchunks = sys.argv[1]



def createOrtho(chunk, doc = Metashape.app.document, orthoRes = 0.05):
    outpath = doc.path[:-4]  # project path without file extension
    crs = Metashape.CoordinateSystem("EPSG::25832")
    
    
    # create mesh
    chunk.resetRegion()
    chunk.buildModel(surface=Metashape.SurfaceType.HeightField, source = Metashape.DataSource.PointCloudData, interpolation = Metashape.Interpolation.EnabledInterpolation, face_count = Metashape.FaceCount.LowFaceCount)
    chunk.smoothModel(25)	
    doc.save()
    
    
    # build ortho
    chunk.resetRegion()
    chunk.buildOrthomosaic(surface=Metashape.ModelData, projection=crs, dx=orthoRes, dy=orthoRes)
    doc.save()
    
    # export ortho
    chunk.resetRegion()
    chunk.exportOrthomosaic(str(outpath + "_" + str(chunk.label) + ".tif"), projection = crs, raster_transform = Metashape.RasterTransformNone,
				write_kml=True, write_world=False, write_alpha=True, tiff_big=True, tiff_compression=Metashape.TiffCompressionNone, white_background=True,dx=orthoRes,dy=orthoRes)
    
    
    
def createOrthoControll(allchunks):  
    print(allchunks)
    if allchunks == "1": 
        for i in Metashape.app.document.chunks:
            createOrtho(chunk = i)
    else:
        createOrtho(chunk = Metashape.app.document.chunk)

        
# RUN CONTROL

createOrthoControll(allchunks)
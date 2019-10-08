#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 10:59:35 2019

@author: uav
"""

import Metashape
import sys

# control: do with all chunks or just the active one
allchunks = sys.argv[1]



def quickAlign(chunk, doc = Metashape.app.document, alignQuality = Metashape.Accuracy.HighAccuracy, kpl = 40000, tpl = 4000):
    
    # quick align photos
    chunk.matchPhotos(accuracy=alignQuality, reference_preselection = True,
                      keypoint_limit = kpl, tiepoint_limit = tpl)
    
    chunk.alignCameras(adaptive_fitting = True)
    chunk.resetRegion()
    
   
    # save document
    doc.read_only = False
    doc.save()
    
   
    


# control: do with all chunks or just the active one
def filterSparseControl(allchunks):  
    print(allchunks)
    if allchunks == "1": 
        for i in Metashape.app.document.chunks:
            quickAlign(chunk = i)
    else:
        quickAlign(chunk = Metashape.app.document.chunk)

        
# RUN CONTROL

filterSparseControl(allchunks)



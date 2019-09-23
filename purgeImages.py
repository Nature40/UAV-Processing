#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:00:09 2019

@author: marvin


"""

import Metashape
# import sys
import glob
import os

# control: do with all chunks or just the active one
# allchunks = sys.argv[1]


def purgeImages(chunk,  doc = Metashape.app.document):
    
    # get list of all images in chunk
    usedImg = []
    for c in chunk.cameras:
        usedImg.append(c.photo.path)
    # get all images
    allImg = glob.glob(os.path.dirname(usedImg[0]) + "/*.JPG")
    rmImg = set(allImg) - set(usedImg)
    
    
    
    print(len(allImg), len(usedImg), len(rmImg))
    return(rmImg)


# run function    
purgeImages(chunk = Metashape.app.document.chunk)  
    
    







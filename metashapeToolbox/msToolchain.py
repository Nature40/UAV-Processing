

import Metashape
import metashapeTools.msSparseCloud as mt

for chunk in Metashape.app.document.chunks:
    mt.createSparse(chunk)



 
## control: do with all chunks or just the active one
#def filterSparseControl(allchunks):  
#    print(allchunks)
#    if allchunks == "1": 
#        for i in Metashape.app.document.chunks:
#            filterSparse(chunk = i)
#    else:
#        filterSparse(chunk = Metashape.app.document.chunk)
#
#        
## RUN CONTROL
#
#
#
#def createOrthoControl(allchunks):  
#    
#
#    if allchunks == "1": 
#        for i in Metashape.app.document.chunks:
#            createOrtho(chunk = i)
#    else:
#        createOrtho(chunk = Metashape.app.document.chunk)
#
#
#filterSparseControl(allchunks)
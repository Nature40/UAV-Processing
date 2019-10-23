# UAV-Processing

The Metashape Toolbox contains workflows for the creation of orthomosaics with Agisoft Metashape.
The workflows consists of Metashape Modules with preconfigured parameters to establish a standardized processing of UAV images.


## Usage

Create a toolchain with functions you find in metashapeTools:


```{python}

import Metashape
import metashapeTools.msSparseCloud as sp
import metashapeTools.msOrtho as ot


chunk = Metashape.app.document.chunk()


# align images and create sparse cloud
mt.createSparse(chunk)

# filter the sparse cloud (ReconstructionUncertainty, ReprojectionError, ProjectionAccuracy)
mt.filteSparse(chunk)

# create a mesh and a orthomosaic
ot.sparse2Ortho(chunk)


```



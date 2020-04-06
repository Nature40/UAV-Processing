#' Seamline cutter
#' 
#' @description Removes the distorted outer parts of the seamlines
#' 
#' @param img sf, image exif data from imgExif
#' @param seam sf, seamline export from Metashape
#' 
#' @import sf
#' @import stringr
#' @import concaveman
#' 
#' 
#' 


seamlineClean = function(img, seam){
  
  # concave hull of images
  ch = concaveman::concaveman(img, concavity = 4)
  # buffer -10 m
  ch = sf::st_buffer(ch, dist = -10)
  
  # check if image positions is 10 m inside the convex hull
  img$inside = t(sf::st_contains(ch, img, sparse = FALSE))
  # remove the last 4 character from string (file ending and .)
  img$name = stringr::str_sub(img$FileName, end = -5)
  
  # throw away outer seamlines
  seam_cut = seam[seam$NAME %in% img$name[img$inside],]
  return(seam_cut)
  
}











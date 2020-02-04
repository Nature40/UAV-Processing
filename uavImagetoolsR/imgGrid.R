#' Sample Image Grid
#' @description Samples a regular grid with equal distance between the images
#'
#' @param imgBB the bounding box to sample
#' @param gridsize distance between the images
#'
#' @return points with regular image location
#'
#' @author Marvin Ludwig
#'
#' @export

#



imgGrid = function(imgBB, gridsize){

  # make sure imgBB is in UTM format
  imgBB = st_transform(imgBB, crs = 25832)

  # sample regular grid
  s = sf::st_make_grid(imgBB, cellsize = gridsize, what = "centers")
  # crop to optimal bounding box
  s = st_intersection(s, imgBB)
  s = st_transform(s, crs = 4326)
  return(s)

}

#' Read Exif from one mission
#' @description Reads the exif data from all images of a flight and returns them as points
#'
#' @param imgPath directory with the images
#'
#' @return sf points of image positions
#'
#' @import exifr
#' @import sf
#'
#' @author Marvin Ludwig
#'
#' @export


imgExif <- function(imgPath){

  # read exif data from images with important exif tags
  img_exif <- exifr::read_exif(imgPath, recursive = TRUE, tags = c("SourceFile", "Directory", "FileName", "DateTimeOriginal",
                                                                "GPSLongitude", "GPSLatitude", "GPSAltitude"))
  # remove points with no GPS signal
  img_exif <- img_exif[!is.na(img_exif$GPSLatitude),]

  # timestamp as POSIXct, order images by date
  img_exif$time <- as.POSIXct(img_exif$DateTimeOriginal, format = "%Y:%m:%d %H:%M:%S")
  img_exif <- img_exif[order(img_exif$time),]

  # add geometry information
  img_exif <- sf::st_as_sf(img_exif, coords = c("GPSLongitude", "GPSLatitude", "GPSAltitude"), crs = 4326 ,dim = "XYZ")
  return(img_exif)
}

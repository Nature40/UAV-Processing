#' Sample points along the flight path
#' @description Samples regular spaced points along the UAV flight path
#'
#' @param task sf points from \code{\link[readTask]{readTask}}
#' @param spacing distance between the sample points
#'
#' @return
#'
#' @author Marvin Ludwig
#'
#' @import dplyr
#' @import sf
#'
#' @export

#




sampleTask <- function(task, spacing = 20){

  # convert to line
  l = task %>% dplyr::summarise(do_union = FALSE) %>% sf::st_cast("LINESTRING")

  # sample regular grid
  l = sf::st_sample(l, size = as.numeric(round(sf::st_length(l) / spacing)), type = "regular")
  l = st_cast(l, to = "POINT")
  return(l)

}


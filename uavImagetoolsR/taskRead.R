#' Read UAV Task
#'
#' @description Reads a UAV mavlink flight task and converts to sf points
#'
#' @param taskfile filepath of the task
#'
#' @author Marvin Ludwig
#'
#' @import sf
#' @export
#'

taskRead <- function(taskfile){

  t <- read.table(taskfile, skip = 1, header = FALSE)
  # filter waypoints
  t <- t[t$V9 != 0,]

  # cut of taxi way
  t <- t[c(which(t$V1 == 7):nrow(t)),]

  t <- sf::st_as_sf(t, coords = c("V10", "V9"), dim = "XY",crs = 4326)
  return(t)
}



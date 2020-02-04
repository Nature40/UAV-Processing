#' Sample Images
#' @description Images at sample poitns
#'
#' @param images bla
#'
#' @return
#'
#' @import sf
#'
#' @author Marvin Ludwig
#'
#' @export

#



sampleImages <- function(images, task, spacing = 20){

  t = sampleTask(task, spacing)
  s = st_nearest_feature(task, images)

  img_sample = images[s,]
  return(img_sample)

}

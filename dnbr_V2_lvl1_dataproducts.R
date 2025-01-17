#
# V2 of Landsat dNBR using Level 1 Data Products
#
# This script is also used to debug the issue with the raster extent encountered
# in the 1st version of this script

# I will refine this script and insert more comments after the code works


# Installing packages 
install.packages("maptools")
install.packages("rgdal")
install.packages("raster")
install.packages("rgeos")
install.packages("rasterVis")
install.packages("Rcurl")
install.packages("devtools")
install.packages("terra")
install.packages("tidyverse")
install.packages("ggspatial")
install.packages("sf")
install.packages("cowplot")
install.packages('mgcv')
install.packages("visreg")
install.packages("utils")
install.packages("Rtools")
install.packages("here")

# From the U.N. Spider tutorial
# I was not successful in running it
install_url("https://github.com/Terradue/rLandsat8/releases/download/v0.1-SNAPSHOT/rLandsat8_0.1.0.tar.gz") 


# Loading libraries for analysis
library(tidyverse)
library(terra)
library(ggspatial)
library(sf)
library(cowplot)
library(mgcv)
library(visreg)
library(raster)
library(rgeos)
library(maptools)
library(rgdal)
library(rasterVis)
library(Rcurl)
library(devtools)
library(rlandsat8)
library(here)
library(rLandsat8)

# Telling 'here' package the top-level directory file path
here::i_am("V2_Script.R")

# Loading source code from Ch. 11 tutorial
# EXTREMELY IMPORTANT that you have this source code
source(here('rasterdf.R'))
# From Ch. 11 tutorial - credited in 1st version of script
options(stringsAsFactors = FALSE)

# Using the 'here' fn to set relative file path names to increase project reproducibility
start_feb <- here('feb_pre_fire')
end_feb <- here('feb_post_fire')

# Creating objects in global environment for prefire imagery and postfire imagery
# Only bands 5 and 7 are in these folders
pre_fire <- list.files(start_feb, full.names = TRUE)
post_fire <- list.files(end_feb, full.names = TRUE)

# Check if directories exist - suggestion from google gemini AI to incorporate checks into the process
if (!dir.exists(here("feb_pre_fire"))) {
  stop("Directory 'feb_pre_fire' does not exist.")
}
if (!dir.exists(here("feb_post_fire"))) {
  stop("Directory 'feb_post_fire' does not exist.")
}
# Stacking the bands and creating a composite raster layer object in global environment
pre_stack <- stack(pre_fire)
post_stack <- stack(post_fire)

# Creating brick object
pre_brick <- brick(pre_stack)
post_brick <- brick(post_stack)

# Plotting Brick as a checkpoint
plot(pre_brick,
     col = gray(20:100 / 100))

plot(post_brick,
     col = gray(20:100 / 100))

# Plotting in RGB to test
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(pre_brick,
        r= 2, g= 1, b= 1,
        stretch = 'lin',
        axes = TRUE,
        main = 'Prefire RGB Composite Image, Bands 5,7')
box(col = 'white')

par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(post_brick,
        r= 2, g= 1, b= 1,
        stretch = 'lin',
        axes = TRUE,
        main = 'Postfire RGB Composite Image, Bands 5,7')
box(col = 'white')

# Calculating the Delta Normalized Burn Ratio Index 
nbr_pre <- 1000 * (pre_brick[[1]] - pre_brick[[2]]) / 
  (pre_brick[[1]] + pre_brick[[2]])

nbr_post <- 1000 * (post_brick[[1]] - post_brick[[2]]) / 
  (post_brick[[1]] + post_brick[[2]])

# Attempt to calculate the Differenced Normalized Burn Ratio Index
dnbr <- (nbr_pre)-(nbr_post)

# Extent error received, trying to combine rasters anyways
nbr_stack <- c(nbr_pre, nbr_post)
names(nbr_stack) <- c("Prefire NBR", "Postfire NBR")
nbr_stack_df <- rasterdf(nbr_stack)


# Plotting the fire severity index of pre & post nbr values as a checkpoint
ggplot(nbr_stack_df) +
  geom_raster(aes(x = x, 
                  y = y, 
                  fill = value)) + 
  scale_fill_gradient(name = "NBR", 
                      low = "lightyellow", 
                      high = "darkgreen") +
  coord_sf(expand = FALSE) +
  annotation_scale(location = 'bl') +
  facet_wrap(facets = vars(variable), 
             ncol = 1) +
  theme_void()

# Creating data frame for dnbr
dnbr_df <- rasterdf(dnbr)

# Classifying the index values into a matrix
rclas <- matrix(c(-Inf, -970, NA,  # Missing data
                  -970, -100, 5,   # Increased greenness
                  -100, 80, 1,     # Unburned
                  80, 265, 2,      # Low severity
                  265, 490, 3,     # Moderate severity
                  490, Inf, 4),    # High severity
                ncol = 3, byrow = T)

severity <- classify(dnbr, rclas)


# Need a shapefile to mask the dnbr data frame to
# Otherwise, we can just plot the entire image
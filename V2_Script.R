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

# 79-85 are relics, the raster package doesn't exist anymore
# Skip these, and use 'terra' package FN 'rast' instead
# pre_stack <- stack(pre_fire)
# post_stack <- stack(post_fire)

# Creating brick object
# pre_brick <- brick(pre_stack)
# post_brick <- brick(post_stack)

# Stacking the bands and creating a composite raster layer object in global environment
pre_stack <- rast(pre_fire)
post_stack <- rast(post_fire)

# Plotting Rasters as a checkpoint
plot(pre_stack,
     col = gray(20:100 / 100))

plot(post_stack,
     col = gray(20:100 / 100))

# Resampling to avoid extent error
pre_stack <- resample(pre_stack,post_stack, method = 'bilinear')

# Plotting in false-color RGB to test
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(pre_stack,
        r= 2, g= 1, b= 1,
        stretch = 'lin',
        axes = TRUE,
        main = 'Prefire RGB Composite Image, Bands 5,7')
box(col = 'white')

par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(post_stack,
        r= 2, g= 1, b= 1,
        stretch = 'lin',
        axes = TRUE,
        main = 'Postfire RGB Composite Image, Bands 5,7')
box(col = 'white') 

# Calculating the Delta Normalized Burn Ratio Index 
nbr_pre <- 1000 * (pre_stack[[1]] - pre_stack[[2]]) / 
  (pre_stack[[1]] + pre_stack[[2]])

nbr_post <- 1000 * (post_stack[[1]] - post_stack[[2]]) / 
  (post_stack[[1]] + post_stack[[2]])

# Attempt to calculate the Differenced Normalized Burn Ratio Index
dnbr <- (nbr_pre)-(nbr_post)

# Resampling nbr_pre and nbr_post
nbr_pre <- resample(nbr_pre,nbr_post, method = 'bilinear')

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

# Plot dnbr without reclassifying dnbr values
ggplot(dnbr_df) +
  geom_raster(aes(x = x, 
                  y = y, 
                  fill = value)) + 
  scale_fill_gradient2(name = "DNBR", 
                       low = "blue", 
                       high = "red",
                       midpoint = 0) +
  coord_sf(expand = F) +
  annotation_scale(location = 'bl') +
  theme_void()

# Re-Classifying the index values into a matrix
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
#
# fire_shape_file <- st_read(file_path,
# quiet = TRUE)

# fire_perimeter <- rasterize(vect(fire_shape_file),
# severity,
# field = "Event_ID")

# severity <- mask(severity,fire_perimeter)

# After reading in shapefile, 
# use this to create dnbr map that is clipped to the fire perimeter
SCcolors = c("darkgreen", 
             "cyan3", 
             "yellow", 
             "red", 
             "green")
SCnames = c("Unburned", 
            "Low", 
            "Moderate", 
            "High", 
            "> Green")
severity_df <- rasterdf(severity)

# Plotting a fire severity map of the imagery
ggplot(severity_df) +
  geom_raster(aes(x = x, 
                  y = y, 
                  fill = as.character(value))) + 
  scale_fill_manual(name = "Severity Class",
                    values = SCcolors,
                    labels = SCnames,
                    na.translate = FALSE) +
  annotation_scale(location = 'bl') +
  coord_fixed(expand = F) +
  theme_void()
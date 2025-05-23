####################################################################################################################
#
# Tutorial for calculating and plotting dNBR Fire Severity Index using Landsat 8/9 satellite imagery
# Adapted by: E. Joel Pimienta
#
# Contributors: Conservation Data Lab, Randy Swaty, Sam Ettenborough
#
# *This tutorial assumes you have referenced data downloaded and in a known file directory*
#                                  OR
# *You have recently downloaded data from USGS EarthExplorer Data base following tutorial by J. Pimienta*
# 
# USGS EarthExplorer Database: https://earthexplorer.usgs.gov/
#
# Adapted from tutorial and book below
# Link to book https://bookdown.org/mcwimberly/gdswr-book/application---wildfire-severity-analysis.html
# Link to tutorial https://www.earthdatascience.org/courses/earth-analytics/multispectral-remote-sensing-data/landsat-data-in-r-geotiff/

###################################################################################################################

# Install all necessary packages for analysis
# install.packages("maptools")
# install.packages("rgdal")
# install.packages("raster")
# install.packages("rgeos")
# install.packages("rasterVis")
# install.packages("Rcurl")
# install.packages("devtools")
# install.packages("terra")
# install.packages("tidyverse")
# install.packages("ggspatial")
# install.packages("sf")
# install.packages("cowplot")
# install.packages('mgcv')
# install.packages("visreg")
# install.packages("utils")
# install.packages("Rtools")

# Load all necessary packages for manipulating raster files, calculating dNBR, and plotting rasters 
# library(tidyverse)
# library(terra)
# library(ggspatial)
# library(sf)
# library(cowplot)
# library(mgcv)
# library(visreg)
# library(raster)
# library(rgeos)
# library(maptools)
# library(rgdal)
# library(rasterVis)
# library(Rcurl)
# library(devtools)
# library(rlandsat8)

options(stringsAsFactors = FALSE)
source("C:\\Users\\joel8\\Dropbox\\My PC (LAPTOP-8RB752PH)\\Documents\\Guat_Fire_Proj\\rasterdf.R")

# ^ from tutorial
# 'rasterdf.R' was the source code provided in Ch. 11 of Geographic Data Science with R
# ^ necessary to have this source code to complete analysis
# A function will appear in your global environment if this code ran properly ('rasterdf')

#############################################################################################
#                                                                                           #
#    PART ONE: IMPORTING LANDSAT .TIF FILES DOWNLOADED FROM USGS EARTHEXPLORER DATABASE     #
#                                               &                                           #
#                CREATE COMPOSITE IMAGES FOR DNBR INDEX CALCULATIONS AND PLOTTING           #
#                                                                                           #
#############################################################################################

# Create an object in the environment for files from the pre-fire satellite imagery
# Creating a separate file directory for pre-fire and post-fire files will be useful
# This portion will demo the process with two file directories with the prefire and postfire files separated prior to importing to R
# See below (line 85) to learn how to subset using glob2rx Fn
#
# Using list.file FN to query file directory and create obj. in global environment (all_prefire + all_postfire)
all_prefire<- list.files("C:\\Users\\joel8\\Dropbox\\My PC (LAPTOP-8RB752PH)\\Documents\\Guat_Fire_Proj\\Feb 2 Rasters",
                         full.names = TRUE)
all_postfire <- list.files("C:\\Users\\joel8\\Dropbox\\My PC (LAPTOP-8RB752PH)\\Documents\\Guat_Fire_Proj\\Feb 26 Rasters",
                           full.names = TRUE)

# Two objects will appear in the global environment and should be a vector with at least 7 characters
##################################################################################################################
#
# Use the glob2rx() Fn to create argument using characters in file path name. Modify the logic to meet your needs
#
# landsat_file_directory <- list.files('file path containing all Landsat data',
#      
#        pattern = glob2rx("B*.tif$"),      # files selected must meet both conditions
#        full.names = TRUE)                 # * indicates the character can be anything 
#                                           # use '$' at the end to get all files that END WITH
#
###################################################################################################################

# The files only show one band of the electromagnetic spectrum (red band, blue band, green band etc.)
# We can plot each individual band or multiple bands using the raster FN and the plot FN
#
# Select one band to plot to demonstrate how each individual band looks
all_prefire [7] 

# For example, the Shortwave-Infrared 2 (Band 7) from Landsat 8
#
# Use the raster FN to convert the file to a raster and plot it
prefire_bandseven <- raster(all_prefire[7])
plot(prefire_bandsix,
     main = 'Prefire Band Six, Central Guatemla',
     col = gray(0:100 / 100))

######################################################################################################################

# Stacking all the band rasters will create a composite image of all 7 rasters
# Using the stack Fn to stack the layers on top of each other, creating a composite image with 7 bands
# Converts the 'vector' object (all_prefire + all_postfire) to a 'RasterLayer' data object (prefire_stack_all +postfire_stack_all)
#
# Stacking the bands
prefire_stack_all <- stack(all_prefire)
postfire_stack_all <- stack(all_postfire)

# Turning the stack into a brick
prefire_brick_all <- brick(prefire_stack_all)
postfire_brick_all <- brick(postfire_stack_all)

# Take a few moments to let the FNs run. They may take 2-5 minutes to run
# View brick attributes to check for errors or other important metadata
prefire_brick_all
postfire_brick_all

##################################################################################################################

# Each raster is now stacked into one raster sandwich with seven bands
# Plot each individual band from prefire and postfire brick
plot(prefire_brick_all,
     col = gray(20:100 / 100))

plot(postfire_brick_all,
     col = gray(20:100 / 100))

# Clean up file naming conventions to make more aesthetic titles
# Print file names to create logic for subsetting
names(prefire_brick_all)

# Select all files using a character argument 'starting with'
names(prefire_brick_all) <- gsub(pattern ='LC08_L2SP_020050_20240202_20240208_02_T1_SR_',replacement =" ",names(prefire_brick_all))
plot(prefire_brick_all,
     col = gray(20:100 / 100))

# Repeating the steps for the postfire elements
names(postfire_brick_all)

# Select all files starting with 'character string'
names(postfire_brick_all) <- gsub(pattern = 'LC09_L2SP_020050_20240226_20240228_02_T1_SR_',replacement = ' ', names(postfire_brick_all))
plot(postfire_brick_all,
     col = gray(20:100 / 100))

#########################################################################################################

# Specify which bands to plot and create composite color images (RGB)
# Plot RGB Composite Band Images using bands 4,3,2
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(prefire_brick_all,
        r= 4, g= 3, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'Prefire RGB Composite Image, Bands 4,3,2')
box(col = 'white')

par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(postfire_brick_all,
        r= 4, g= 3, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'Postfire RGB Composite Image, Bands 4,3,2')
box(col = 'white')

# Plot a prefire false color composite using bands 7,5,2 to calculate the dNBR Index
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(prefire_brick_all,
        r= 7, g= 5, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'False Color Composite Image, Bands 7,5,2')
box(col = 'white')

#Repeat the process to create a postfire false color composite using bands 7,5,2 to calculate the dNBR Index
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(postfire_brick_all,
        r= 7, g= 5, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'False Color Composite Image, Bands 7,5,2')
box(col = 'white')

# YOU HAVE REACHED THE END OF PART ONE:IMPORTING LANDSAT .TIF FILES DOWNLOADED FROM USGS EARTHEXPLORER DATABASE ############################
# AND CREATE COMPOSITE IMAGES FOR DNBR INDEX CALCULATIONS AND PLOTTING 

#################################################################################################################################################
#################################################################################################################################################
#
# Beginning PART TWO of the tutorial
#
#############################################################################################
#                                                                                           #
#                                                                                           #
#  PART 2: CALCULATING AND PLOTTING THE DNBR INDEX USING LANDSAT SATELLITE IMAGERY          #                                        #
#                                                                                           #
#                                                                                           #
#############################################################################################
#
# All neccesary packages were loaded in PART ONE of the tutorial
# You have created a composite raster object (prefire_brick_all + postfire_brick_all) in PART ONE of the tutorial
# 
# The bands used for dNBR fire severity classification are:
#
# Band 7: Shorwave-Infrared 2
# Band 5: Near-Infrared 
# Band 2: Blue
# 
# You will use them in place of the red, green, and blue bands, respectively

# Refer to this section or the USGS Landsat 8 link here https://www.usgs.gov/landsat-missions/landsat-8
# Modify the bands you use for your study purposes. Other indices use multi-band satellite imagery to create maps
###############################################################################################################################

# Plot a false color composite using bands 7,5,2 to calculate the dNBR Index ###################################
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(prefire_brick_all,
        r= 7, g= 5, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'Prefire False Color Composite Image, Bands 7,5,2')
box(col = 'white')

#Repeat the process to create a postfire false color composite using bands 7,5,2 to calculate the dNBR Index
par(col.axis = 'white', col.lab = 'white', tck = 0)
plotRGB(postfire_brick_all,
        r= 7, g= 5, b= 2,
        stretch = 'lin',
        axes = TRUE,
        main = 'Postfire False Color Composite Image, Bands 7,5,2')
box(col = 'white')

################################################################################################################
#
# Calculating the Differenced Normalized Burn Ratio Index using the false color composites
nbr_pre <- 1000 * (prefire_brick_all[[5]] - prefire_brick_all[[7]]) / 
  (prefire_brick_all[[5]] + prefire_brick_all[[7]])

nbr_post <- 1000 * (postfire_brick_all[[5]] - postfire_brick_all[[7]]) / 
  (postfire_brick_all[[5]] + postfire_brick_all[[7]])

# Attempt to calculate the Differenced Normalized Burn Ratio Index
dnbr <- (nbr_pre) - (nbr_post)

# YOU WILL RECIEVE A WARNING MESSAGE, BUT THIS IS EXPECTED
# CONTINUE FOLLOWING THE TUTORIAL #############################################################
# You will get a warning pasted below:
# 'Warning message:
#   In nbr_pre - nbr_post :
# Raster objects have different extents. Result for their intersection is returned
#
# IMPORTANT: YOU NEED TO RECIEVE THIS WARNING TO CONTINUE
# 'results for their intersection is returned' INDICATES THE CALCULATION WAS SUCCESSFUL
#
# This occurs because each image will not have perfect overlap
# Confirm that the Coordinate Reference System (crs) and resolution are the same
# nbr_pre
# nbr_post

# > nbr_pre 
# class      : RasterLayer 
# dimensions : 7711, 7551, 58225761  (nrow, ncol, ncell)
# resolution : 30, 30  (x, y)
# extent     : 619785, 846315, 1483185, 1714515  (xmin, xmax, ymin, ymax)
# crs        : +proj=utm +zone=15 +datum=WGS84 +units=m +no_defs 
# source     : memory
# names      : layer 
# values     : -741.8728, 444.0148  (min, max)
#
# > nbr_post
# class      : RasterLayer 
# dimensions : 7701, 7541, 58073241  (nrow, ncol, ncell)
# resolution : 30, 30  (x, y)
# extent     : 620385, 846615, 1483485, 1714515  (xmin, xmax, ymin, ymax)
# crs        : +proj=utm +zone=15 +datum=WGS84 +units=m +no_defs 
# source     : memory
# names      : layer 
# values     : -737.1108, 632.0712  (min, max)
#
# Both raster data frames have the same crs (UTM and WGS84)
# Both raster data frames have 30x30 resolution
# However, they have different extents nbr_pre (619785, 846315, 1483185, 1714515) and nbr_post (620385, 846615, 1483485, 1714515)
#
# ONLY DO THIS STEP IF YOU RECIVE ERRORS
# OTHERWISE, SKIP TO NEXT SECTION
#
# Use the resample FN to match the extents (Substitute the 'method' argument with 'bilinear' OR 'ngb')
# resample_nbr_post <- resample(nbr_post, nbr_pre, method='ngb')

# The mask FN can be used followed by the crop FN to crop the raster to a specified extent
# masked_nbr_post <- mask(nbr_post, nbr_pre)
# cropped_nbr_post <- crop(masked_nbr_post, nbr_pre)
#
###########################################################################################
#
# Combine the two rasters into one composite image
nbr_stack <- c(nbr_pre, nbr_post)
names(nbr_stack) <- c("Prefire NBR", "Postfire NBR")
nbr_stack_df <- rasterdf(nbr_stack)

# Plotting the dNBR raster
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
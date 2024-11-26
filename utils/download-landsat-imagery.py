import ee
import numpy as np
import matplotlib.pyplot as plt
import urllib
from PIL import Image

# this function is a wrapper of the ee.Initalize function so it can more easliy
# be export to the R environment the project using the Google Earth Engine API
###### not sure this needed
def initialize_project(ee_project_name):
    ###### will want to add error handling here
    print('Connecting ot Earth Enginer API...')
    ee.Initialize(project = ee_project_name)
    print(ee.String('Hello from the Earth Engine servers!').getInfo())
 
# ee.Initialize(project='ee-samettenborough')

# will this have access to ee (scopewise)?
def generate_area_of_interest(latitude, longitude, buffer_size_meters):
    return ee.Geometry.Point([longitude, latitude]).buffer(buffer_size_meters)

# # Define the area of interest
# guat_coords = [-90.5069, 14.6349]  # Longitude, Latitude
# aoi = ee.Geometry.Point(guat_coords).buffer(5000)  # Buffer of 5 km

# Get a Landsat 8 image collection
landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA")  # Top of Atmosphere reflectance
landsat_filtered = (
    landsat.filterBounds(aoi)  # Filter by location
    .filterDate("2023-01-01", "2023-12-31")  # Filter by date (2023 as an example)
    .sort("CLOUD_COVER")  # Sort by cloud cover
    .first()  # Get the least cloudy image
)

# Get the RGB bands
image = ee.Image(landsat_filtered).select(["B4", "B3", "B2"])  # Red, Green, Blue bands

# Define visualization parameters
vis_params = {
    "min": 0,
    "max": 0.3,  # TOA reflectance is typically scaled between 0 and 1
    "bands": ["B4", "B3", "B2"],
}

# Download the image as a numpy array
url = image.getThumbURL({
    "region": aoi.bounds().getInfo()["coordinates"],  # Specify the area to download
    "dimensions": [512, 512],  # Specify image resolution
    **vis_params,
})
print("Image download URL:", url)

# Read the image from the URL using urllib and Pillow
with urllib.request.urlopen(url) as response:
    img = Image.open(response)
    
# Alternatively, plot the image directly
# Get the image as a numpy array
rgb_img = np.array(img)

# Plot the image
plt.figure(figsize=(10, 10))
plt.imshow(rgb_img)
plt.title("Landsat 8 Image - Guatemala City, Guatemala")
plt.axis("off")
plt.show()

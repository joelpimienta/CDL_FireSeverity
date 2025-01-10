import ee
import numpy as np
import matplotlib.pyplot as plt
import urllib
import requests
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
# tier 1 is highest quality tier
# surface reflectance has been corrected for atmospheric conditions such as
# aerosol scattering - may be better for comparing same scene over time
# top of atmosphere can have atmospheric conditions that cause distortions
# landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")  # Surface Reflectance
# landsat_filtered = (
#     landsat.filterBounds(aoi)  # Filter by location
#     .filterDate("2023-01-01", "2023-12-31")  # Filter by date (2023 as an example)
#     .sort("CLOUD_COVER")  # Sort by cloud cover
#     .first()  # Get the least cloudy image
# )

def get_filtered_image_collection(image_collection, aoi, start_date, end_date):
    landsat = ee.ImageCollection(image_collection)
    landsat_filtered = (
        landsat.filterBounds(aoi)
        .filterDate(start_date, end_date)
        # do we want filter here or outside of here?
        .sort("CLOUD_COVER")
        .first()
    )
    return landsat_filtered

lat = 14.6349
lon = -90.5069
initialize_project("ee-samettenborough")
# point is for guatamela city
aoi = generate_area_of_interest(lat, lon, 5000)
image = get_filtered_image_collection(
    "LANDSAT/LC08/C02/T1_L2",
    aoi,
    "2023-01-01",
    "2023-12-31"
)

# Select bands for visualization (Red, Green, Blue)
rgb_bands = ["SR_B4", "SR_B3", "SR_B2"]

# Export each band directly to local
for band in rgb_bands:
    single_band = image.select(band)
    
    # Get the download URL for the image
    url = single_band.getDownloadURL({
        'scale': 30,  # 30m resolution
        'region': aoi.getInfo(),  # Define export region
        'format': 'GeoTIFF'
    })
    
    print(f"Downloading {band} from {url}")
    
    # Download the file
    response = requests.get(url, stream=True)
    output_file = f"data/{band}_GuatemalaCity.tif"
    with open(output_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print(f"Saved {band} to {output_file}")


# 
# 
# 
# vis_params = {"min": 0, "max": 10000, "bands": rgb_bands}
# 
# import folium
# import geemap.core as geemap
# 
# image_rgb = image.visualize(bands=['SR_B5', 'SR_B4', 'SR_B3'], max=0.5)
# # Define a map centered on San Francisco Bay.
# map_mosaic = geemap.Map(center=[lat, lon], zoom=10)
# 
# # Add the image layer to the map and display it.
# map_mosaic.add_layer(image_rgb, None, 'mosaic')
# 
# display(map_mosaic)
# ndwi_rgb = ndwi_masked.visualize(min=0.5, max=1, palette=['00FFFF', '0000FF'])
# 
# # Add the image to a map for visualization using Folium
# def add_ee_layer(map_object, ee_image, vis_params, name):
#     map_id_dict = ee.Image(ee_image).getMapId(vis_params)
#     folium.raster_layers.TileLayer(
#         tiles=map_id_dict["tile_fetcher"].url_format,
#         attr="Google Earth Engine",
#         name=name,
#         overlay=True,
#         control=True
#     ).add_to(map_object)
# 
# # Get the RGB bands
# image = image.select(["SR_B4", "SR_B3", "SR_B2"])  # Red, Green, Blue bands
# image
# # Create a map
# map_guatemala = folium.Map(location=[lat, lon], zoom_start=13)
# map_guatemala
# 
# # Add the Landsat image to the map
# add_ee_layer(map_guatemala, image, vis_params, "Guatemala City Landsat Image")
# 
# # Add layer control
# folium.LayerControl().add_to(map_guatemala)
# 
# # Display the map
# map_guatemala.save("guatemala_city_landsat_map.html")
# display(Image(filename="guatemala_city_landsat_map.html"))
# 
# # If you also want to plot the image with matplotlib
# def plot_landsat_image(image, vis_params):
#     url = image.getThumbURL({
#         'min': vis_params['min'],
#         'max': vis_params['max'],
#         'bands': vis_params['bands'],
#         'region': aoi,
#         'dimensions': 512
#     })
#     img_data = plt.imread(url)
#     plt.figure(figsize=(10, 10))
#     plt.imshow(img_data)
#     plt.axis('off')
#     plt.title("Guatemala City - Landsat 8 RGB")
#     plt.show()
# 
# plot_landsat_image(image, vis_params)
# 
# image
# 
# # Define visualization parameters
# vis_params = {
#     "min": 0,
#     "max": 0.3,  # TOA reflectance is typically scaled between 0 and 1
#     "bands": ["SR_B4", "SR_B3", "SR_B2"],
# }
# 
# # Download the image as a numpy array
# url = image.getThumbURL({
#     "region": aoi.bounds().getInfo()["coordinates"],  # Specify the area to download
#     "dimensions": [512, 512],  # Specify image resolution
# })
# print("Image download URL:", url)
# 
# # Read the image from the URL using urllib and Pillow
# with urllib.request.urlopen(url) as response:
#     img = Image.open(response)
# 
# img
# # Alternatively, plot the image directly
# # Get the image as a numpy array
# rgb_img = np.array(img)
# 
# # Plot the image
# plt.figure(figsize=(10, 10))
# plt.imshow(rgb_img)
# plt.title("Landsat 8 Image - Guatemala City, Guatemala")
# plt.axis("off")
# plt.show()
# 

import ee
import numpy as np
import matplotlib.pyplot as plt
import urllib
import requests
import os
from PIL import Image

# this function is a wrapper of the ee.Initalize function so it can more easliy
# be export to the R environment the project using the Google Earth Engine API
###### not sure this needed
def initialize_project(ee_project_name):
    ###### will want to add error handling here
    print('Connecting to Earth Engine API...')
    ee.Authenticate()
    ee.Initialize(project = ee_project_name)
    print(ee.String('Hello from the Earth Engine servers!').getInfo())
 
# ee.Initialize(project='ee-samettenborough')

# will this have access to ee (scopewise)?
def generate_area_of_interest(latitude, longitude, buffer_size_meters):
    return ee.Geometry.Point([longitude, latitude]).buffer(buffer_size_meters)
  
# Generate a grid of AOIs from a larger AOI
def create_grid(aoi, grid_size_km):
  # Convert grid size from kilometers to degrees
  grid_size_degrees = grid_size_km / 113.32
  aoi_bounds = aoi.bounds().getInfo()["coordinates"][0]
  min_x, min_y = aoi_bounds[0]
  max_x, max_y = aoi_bounds[2]
    
  print("min_vals", min_x, min_y)
  print("max_vals", max_x, max_y)

    
  grid = []
  x = min_x
    
  while x < max_x:
      print("x", x)
      y = min_y
      while y < max_y:
          print("y", y)
          grid_cell = ee.Geometry.Rectangle(
              [x, y, min(x + grid_size_degrees, max_x), min(y + grid_size_degrees, max_y)]
          )
          grid.append(grid_cell)
          y += grid_size_degrees
          print("ending y", y)
      x += grid_size_degrees
    
  print("ending grid", grid)

  return grid

# Filter an image collection by AOI and date, and return the least cloudy image
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
  
  # Download the image for each band
def download_image(image, bands, aoi, resolution, output_folder, prefix):
    for band in bands:
        single_band = image.select(band)
        url = single_band.getDownloadURL({
            "scale": resolution,
            "region": aoi.getInfo(),
            "format": "GeoTIFF"
        })

        output_file = os.path.join(output_folder, f"{prefix}_{band}.tif")
        print(f"Downloading {band} from {url} to {output_file}")
        
        response = requests.get(url, stream=True)
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Saved {band} to {output_file}")
        
# Main processing
def process_large_aoi():
    initialize_project("ee-samettenborough")

    # Define the large AOI
    # guat city
    lat, lon = 14.6349, -90.5069
    # 30m resolution
    resolution = 30
    # define area of interest, uses 100,000 km2 buffer here
    aoi = ee.Geometry.Point([lon, lat]).buffer(100000)

    # Split the AOI into a grid of 10,000 km² chunks
    grid_size_km = 1000
    grid = create_grid(aoi, grid_size_km)
    
    return(grid)

    # Output folder
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)
    
    print("there")

    # Process each chunk
    for i, chunk in enumerate(grid):
        print(f"Processing chunk {i + 1}/{len(grid)}")
        image = get_filtered_image_collection(
            "LANDSAT/LC08/C02/T1_L2",
            chunk,
            "2023-01-01",
            "2023-12-31"
        )

        if image is not None:
            bands = ["SR_B4", "SR_B3", "SR_B2"]  # Red, Green, Blue
            prefix = f"chunk_{i + 1}"
            download_image(image, bands, chunk, resolution, output_folder, prefix)
        else:
            print(f"No image found for chunk {i + 1}")

temp = process_large_aoi()

lat = 14.6349
# Latitude of Guatemala City
lon = -90.5069
# Longitude of Guatemala City
resolution = 30  
# Resolution in meters
max_pixels = 4000
# Max pixel grid dimensions

initialize_project("ee-samettenborough")

# Generate the AOI
aoi = generate_area_of_interest(lat, lon, 100000)

# Get the Landsat 8 image
image = get_filtered_image_collection(
  "LANDSAT/LC08/C02/T1_L2",
  aoi,
  "2023-01-01",
  "2023-12-31"
)
    
# Define RGB bands for visualization
rgb_bands = ["SR_B4", "SR_B3", "SR_B2"]

# Calculate the maximum tile size
max_tile_size = calculate_max_tile_size(max_pixels, resolution)
print(f"Max tile size in degrees: {max_tile_size}")

# Split the AOI into tiles
tiles = split_aoi(aoi, max_tile_size)
print(f"Generated {len(tiles)} tiles.")

# Download images for each tile and band
for i, tile in enumerate(tiles):
  for band in rgb_bands:
    single_band = image.select(band)
    
    try:
      # Get the download URL for the tile
      url = single_band.getDownloadURL({
        'scale': 30,  # 30m resolution
        'region': tile.getInfo(),  # Export region for the tile
        'format': 'GeoTIFF'
      })
        
      print(f"Downloading {band} for tile {i} from {url}")
        
      # Download the file
      response = requests.get(url, stream=True)
      output_file = f"data/{band}_Tile{i}.tif"
      with open(output_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
          file.write(chunk)
          print(f"Saved {band} for tile {i} to {output_file}")
            
    except Exception as e:
      print(f"Error downloading {band} for tile {i}: {e}")

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

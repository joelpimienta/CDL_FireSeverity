import ee
import os
import requests

# Initialize Earth Engine
def initialize_earth_engine(ee_project_name):
    print("Authenticating Earth Engine...")
    ee.Authenticate()
    ee.Initialize(project = ee_project_name)
    print("Earth Engine Initialized!")

# Get Guatemala's boundary
def get_guatemala_boundary():
    countries = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
    guatemala = countries.filter(ee.Filter.eq("country_na", "Guatemala")).geometry()
    return guatemala

def create_aoi(coordinates):
  aoi = ee.Geometry.Polygon(coordinates)
  return aoi

# Split the AOI into tiles
def create_tiles(aoi, grid_size_km):
    grid_size_degrees = grid_size_km / 111.32  # Approximation for latitude
    bounds = aoi.bounds().getInfo()["coordinates"][0]
    min_x, min_y = bounds[0]
    max_x, max_y = bounds[2]

    tiles = []
    x = min_x
    while x < max_x:
        y = min_y
        while y < max_y:
            chunk = ee.Geometry.Rectangle([
                x,
                y,
                min(x + grid_size_degrees, max_x),
                min(y + grid_size_degrees, max_y)
            ])
            tiles.append(chunk)
            y += grid_size_degrees
        x += grid_size_degrees

    return tiles

# Get the least cloudy Landsat 8 image for a given AOI
def get_least_cloudy_image(aoi, start_date, end_date):
    collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    filtered = (
        collection.filterBounds(aoi)
        .filterDate(start_date, end_date)
        .sort("CLOUD_COVER")
    )
    return filtered.first()

# Function to download each band as a separate .tif file
def download_image(image, bands, aoi, folder, prefix):
      image = image.select(bands)
      
      try:
          # Generate download URL for the single band
          url = image.getDownloadURL({
              "scale": 30,  # 30m resolution
              "region": aoi.getInfo(),  # Export region
              "format": "GeoTIFF",
          })
          print(f"Downloading {prefix}_rgb from {url}")
          
          # Perform the download
          response = requests.get(url, stream=True)
          os.makedirs(folder, exist_ok=True)
          file_path = os.path.join(folder, f"{prefix}_rgb.tif")
          
          with open(file_path, "wb") as file:
              for chunk in response.iter_content(chunk_size=8192):
                  file.write(chunk)
          
          print(f"Saved {prefix}_rgb to {file_path}")
      
      except Exception as e:
          print(f"Error downloading rgb for {prefix}: {e}")
            
def process_aoi(coordinates, grid_size_km, output_folder, start_date, end_date):
    initialize_earth_engine("ee-samettenborough")
    
    # Get Guatemala's boundary
    aoi = create_aoi(coordinates)
    
    # Split into tiles
    tiles = create_tiles(aoi, grid_size_km)
    
    # Process each tile
    for i, tile in enumerate(tiles):
        print(f"Processing tile {i + 1}/{len(tiles)}")
        image = get_least_cloudy_image(tile, start_date, end_date)
        
        if image:
            bands = ["SR_B4", "SR_B3", "SR_B2"]  # Red, Green, Blue
            prefix = f"guatemala_tile_{i + 1}"
            download_image(image, bands, tile, output_folder, prefix)
        else:
            print(f"No image found for tile {i + 1}")
            


# Main function to process Guatemala
def process_guatemala():
    initialize_earth_engine("ee-samettenborough")
    
    # Get Guatemala's boundary
    guatemala = get_guatemala_boundary()
    
    # Split into tiles
    grid_size_km = 10  # 100 km per tile
    tiles = create_tiles(guatemala, grid_size_km)
    print(f"Created {len(tiles)} tiles for Guatemala.")

    # Output folder
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)
    
    # Process each tile
    for i, tile in enumerate(tiles[0:20]):
        print(f"Processing tile {i + 1}/{len(tiles)}")
        image = get_least_cloudy_image(tile, "2023-01-01", "2023-12-31")
        
        if image:
            bands = ["SR_B4", "SR_B3", "SR_B2"]  # Red, Green, Blue
            prefix = f"guatemala_tile_{i + 1}"
            download_image(image, bands, tile, output_folder, prefix)
        else:
            print(f"No image found for tile {i + 1}")
            

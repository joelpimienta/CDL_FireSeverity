import ee
import geemap
import pandas as pd
from datetime import datetime
import os

def create_fishnet_and_download(
    image,
    region,
    out_dir,
    rows=2,
    cols=2,
    prefix="landsat_",
    crs="EPSG:3857",
    scale=30
):
    """
    Creates a fishnet grid and downloads image tiles without visualization
    
    Parameters:
    image (ee.Image): Earth Engine image to download
    region (ee.Geometry): Region to download
    out_dir (str): Output directory path
    rows (int): Number of rows in the grid
    cols (int): Number of columns in the grid
    prefix (str): Prefix for output filenames
    crs (str): Coordinate reference system
    scale (int): Resolution in meters
    """
    # Create fishnet grid
    features = geemap.fishnet(region, rows=rows, cols=cols)
    
    # Download tiles
    geemap.download_ee_image_tiles(
        image=image,
        features=features,
        out_dir=out_dir,
        prefix=prefix,
        crs=crs,
        scale=scale,
        bands=
    )

def process_aoi(coordinates, output_folder, start_date, end_date):
    
    # Initialize Earth Engine
  ee.Authenticate()
  ee.Initialize(project = "ee-samettenborough")
  
  # Load the image
  image = ee.Image("LANDSAT/LC08/C02/T1_L2")
  
  print(coordinates)
  
  # Define region (Guatemala example)
  region = ee.Geometry.BBox(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
  
  # Create fishnet and download tiles
  create_fishnet_and_download(
      image=image,
      region=region,
      out_dir=output_folder,
      rows=2,
      cols=2,
      prefix="landsat_",
      scale=30
  )
  
  print(f"Download complete. Files saved to: {output_folder}")

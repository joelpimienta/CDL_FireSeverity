import ee
import geemap

# create a bounding box given a set of lat/long values
#
# Parameters:
#   coordinates (list): a list containing the top left and bottom right
#     corners of a bounding box in the format [lat, long, lat, long]
def create_bounding_box(coordinates):
    # https://stackoverflow.com/questions/7745952/how-to-expand-a-list-to-function-arguments-in-python
    region = ee.Geometry.BBox(*coordinates)
    return region
  
# create a composite image of a region from a set of images in a given time
# window where each pixel is a less cloudy pixel from that collection
#
# Parameters: 
#   start_date (str): date as a string in yyyy-mm-dd format representing the
#     start of the time window to search for images within
#   end_date (str): date as a string in yyyy-mm-dd format representing the end
#     of the time window to search for images within
#   region (ee.BBox): the region created from the function above
def create_composite_image(start_date, end_date, region, filter_lim):
  
    # Load the LANDSAT/LC08/C02/T1_L2 collection and filter it
    collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
        .filterDate(start_date, end_date) \
        .filterBounds(region) \
        .filter(ee.Filter.lte('CLOUD_COVER', filter_lim))
    
    # Create a cloud-free composite using the median reducer
    composite = collection.median() \
        .select(['SR_B5', 'SR_B7'])
    
    return composite
  

# create a fishnet grid and downloads image tiles without visualization
#
# Parameters:
#   image (ee.Image): Earth Engine image to download
#   region (ee.Geometry): Region to download
#   out_dir (str): Output directory path
#   rows (int): Number of rows in the grid
#   cols (int): Number of columns in the grid
#   prefix (str): Prefix for output filenames
#   crs (str): Coordinate reference system
#   scale (int): Resolution in meters
def create_fishnet_and_download(
    image,
    region,
    out_dir,
    rows,
    cols,
    prefix,
    crs,
    scale
):
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
    )

# create a wrapper function that calls the above functions in the correct
# sequence
#
# Parameters:
#   project (str): the name of the GEE project to authenticate
#   coordinates (list): a list containing the top left and bottom right
#     corners of a bounding box in the format [lat, long, lat, long]
#   start_date (str): date as a string in yyyy-mm-dd format representing the
#     start of the time window to search for images within
#   end_date (str): date as a string in yyyy-mm-dd format representing the end
#     of the time window to search for images within
#   out_dir (str): Output directory path
#   filter_lim (int): set the limit of clouds allowed in an image collection
#   rows (int): Number of rows in the grid
#   cols (int): Number of columns in the grid
#   prefix (str): Prefix for output filenames
#   crs (str): Coordinate reference system
#   scale (int): Resolution in meters
def process_aoi(
    project,
    coordinates,
    start_date,
    end_date,
    out_dir,
    filter_lim=20,
    rows=2,
    cols=2,
    prefix="landsat_",
    crs="EPSG:3857",
    scale=30
    ):
    
    # Initialize Earth Engine
  ee.Authenticate()
  ee.Initialize(project = project)
  
  region = create_bounding_box(coordinates)
  composite = create_composite_image(start_date, end_date, region, filter_lim)
  create_fishnet_and_download(
    composite,
    region, 
    out_dir,
    rows,
    cols,
    prefix,
    crs,
    scale
  )
  
  print(f"Download complete. Files saved to: {out_dir}")

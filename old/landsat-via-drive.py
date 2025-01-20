import ee

# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project = "ee-samettenborough")

portland_geometry = ee.Geometry.Point([-122.6765, 45.5231]).buffer(50000)  # 50 km radius buffer around Portland
# Define time range (May 2024)
start_date = '2024-05-01'
end_date = '2024-05-31'

# Load Landsat 8 Level 2 image collection
landsat_collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
    .filterBounds(portland_geometry) \
    .filterDate(start_date, end_date) \
    .sort('CLOUD_COVER')  # Sort by cloud cover

# Select RGB bands and the least cloudy image
rgb_bands = ['SR_B4', 'SR_B3', 'SR_B2']  # Surface reflectance (red, green, blue)
least_cloudy_image = landsat_collection.first().select(rgb_bands)

# Visualize parameters (optional for mapping)
visualization_params = {
    'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
    'min': 0,
    'max': 3000,
    'gamma': 1.4,
}

# Export the image
export_task = ee.batch.Export.image.toDrive(
    image=least_cloudy_image.clip(oregon_geometry),
    description='Landsat8_Oregon_May2024',
    folder='EarthEngineExports',
    scale=30,  # 30-meter resolution
    region=portland_geometry,
    maxPixels=1e13
)

export_task.start()
print("Export started. Check your Google Drive for the result.")

ee.data.getTaskStatus("463IWZQJ76TQDNBI6DNOZQVT")

export_task

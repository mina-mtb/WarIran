import ee
import os
from dotenv import load_dotenv

class GEEHandler:
    """
    Handles connection and data retrieval from Google Earth Engine (GEE).
    Focuses on Sentinel-1 (SAR) and Sentinel-2 (Optical).
    """
    
    def __init__(self):
        self.project_id = os.getenv("EE_PROJECT_ID")
        
    def authenticate(self):
        """
        Initializes the Earth Engine library.
        Assumes the user has already authenticated via CLI or service account.
        """
        try:
            if self.project_id:
                ee.Initialize(project=self.project_id)
            else:
                ee.Initialize()
            print("GEE Status: Successfully initialized.")
            return True
        except Exception as e:
            print(f"GEE Status: Initialization failed. Error: {e}")
            print("Tip: Run 'earthengine authenticate' in your terminal.")
            return False

    def get_latest_sar_pair(self, lon, lat, radius_km=1.0):
        """
        Retrieves the two most recent Sentinel-1 images for comparison.
        """
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(radius_km * 1000).bounds()
        
        # Filter Sentinel-1 GRD collection
        collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
                      .filterBounds(roi)
                      .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
                      .filter(ee.Filter.eq('instrumentMode', 'IW'))
                      .sort('system:time_start', False))
        
        images = collection.toList(2)
        return ee.Image(images.get(0)), ee.Image(images.get(1))

    def detect_structural_change(self, pre_img, post_img, lon, lat, radius_km=0.5):
        """
        Compares two SAR images to detect significant backscatter changes.
        """
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(radius_km * 1000).bounds()
        
        # Ratio method is common for SAR change detection
        # We look for significant drops in backscatter (damage)
        diff = post_img.select('VV').subtract(pre_img.select('VV'))
        
        stats = diff.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.stdDev(),
                sharedInputs=True
            ),
            geometry=roi,
            scale=10
        )
        
        return stats.getInfo()

    def get_latest_optical(self, lon, lat, radius_km=1.0):
        """
        Retrieves the latest cloud-free Sentinel-2 image.
        """
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(radius_km * 1000).bounds()
        
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterBounds(roi)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                      .sort('system:time_start', False))
        
        return collection.first()

if __name__ == "__main__":
    load_dotenv()
    handler = GEEHandler()
    if handler.authenticate():
        print("Earth Engine is ready for Phase 2!")
        # Test: Get latest SAR info for a point in Tehran
        img1, img2 = handler.get_latest_sar_pair(51.3890, 35.6892)
        if img1 and img2:
            print(f"Latest SAR Image Date: {img1.date().format('YYYY-MM-DD').getInfo()}")
            print(f"Previous SAR Image Date: {img2.date().format('YYYY-MM-DD').getInfo()}")

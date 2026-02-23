import requests
import pandas as pd
import os
from io import StringIO
from datetime import datetime, timedelta

class ThermalHandler:
    """
    Handles data fetching from NASA FIRMS (Fire Information for Resource Management System).
    Provides Near Real-Time (NRT) thermal anomaly detection.
    """
    
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
    
    def __init__(self):
        self.api_key = os.getenv("FIRMS_API_KEY")
        # Default bounding box for Iran (West, South, East, North)
        self.default_bbox = "44.0,25.0,63.5,40.0"
        
    def fetch_recent_hotspots(self, range_days=1, bbox=None):
        """
        Fetches thermal hotspots for the last X days in a specific area.
        """
        if not self.api_key or "your_firms_key" in str(self.api_key):
            print("Error: Valid FIRMS_API_KEY not found in environment. Please add it to your .env file.")
            return None
            
        target_bbox = bbox if bbox else self.default_bbox
        # Source can be VIIRS_SNPP_NRT, VIIRS_NOAA20_NRT, or MODIS_NRT
        source = "VIIRS_SNPP_NRT"
        url = f"{self.BASE_URL}/{self.api_key}/{source}/{target_bbox}/{range_days}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Check for error messages in the CSV text
            if "Invalid API call" in response.text:
                print(f"FIRMS API Error: {response.text.strip()}")
                return None
                
            # Parse CSV data
            df = pd.read_csv(StringIO(response.text))
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from FIRMS: {e}")
            return None

    def filter_by_coordinates(self, df, lat_min, lat_max, lon_min, lon_max):
        """
        Filters the hotspots to a specific bounding box (e.g., a city or specific area).
        """
        if df is None or df.empty:
            return df
            
        filtered = df[
            (df['latitude'] >= lat_min) & 
            (df['latitude'] <= lat_max) & 
            (df['longitude'] >= lon_min) & 
            (df['longitude'] <= lon_max)
        ]
        return filtered

if __name__ == "__main__":
    # Test block
    from dotenv import load_dotenv
    load_dotenv()
    
    handler = ThermalHandler()
    print("Fetching hotspots for Iran...")
    data = handler.fetch_recent_hotspots()
    if data is not None:
        print(f"Found {len(data)} potential hotspots in the last 24 hours.")
        print(data.head())

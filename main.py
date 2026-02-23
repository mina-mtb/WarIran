import time
import os
from dotenv import load_dotenv
from engine.thermal_handler import ThermalHandler
from engine.gee_handler import GEEHandler

def main():
    load_dotenv()
    print("--- WarIran Monitoring Engine ---")
    print("Status: Initializing components...")
    
    thermal_engine = ThermalHandler()
    gee_engine = GEEHandler()
    
    if not gee_engine.authenticate():
        print("Warning: GEE authentication failed. Satellite verification will be disabled.")
    
    # Placeholder for a user's target area (e.g., Tehran center)
    TARGET_LAT = 35.6892
    TARGET_LON = 51.3890
    RADIUS = 0.5 # approx 50km box for testing
    
    print(f"Status: Monitoring started for Coordinates ({TARGET_LAT}, {TARGET_LON})")
    
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running periodic check...")
        
        # 1. Check Thermal Anomalies (NASA FIRMS)
        hotspots = thermal_engine.fetch_recent_hotspots(range_days=1)
        if hotspots is not None and not hotspots.empty:
            local_events = thermal_engine.filter_by_coordinates(
                hotspots, 
                TARGET_LAT - RADIUS, TARGET_LAT + RADIUS,
                TARGET_LON - RADIUS, TARGET_LON + RADIUS
            )
            
            if not local_events.empty:
                print(f"ALERT: Found {len(local_events)} thermal anomalies!")
                
                # 2. Trigger Satellite Verification (GEE SAR)
                for index, event in local_events.iterrows():
                    e_lat, e_lon = event['latitude'], event['longitude']
                    print(f"Analyzing Event at ({e_lat}, {e_lon})...")
                    
                    pre, post = gee_engine.get_latest_sar_pair(e_lon, e_lat)
                    if pre and post:
                        change_stats = gee_engine.detect_structural_change(pre, post, e_lon, e_lat)
                        print(f"Structural Change Stats: {change_stats}")
                        
                        # TODO: Calculate probability of damage based on backscatter drop
                        # TODO: Trigger Telegram Notification with combined data
            else:
                print("Status: No thermal anomalies detected.")
        
        # Sleep for the interval
        interval = int(os.getenv("CHECK_INTERVAL_SECONDS", 3600))
        time.sleep(interval)

if __name__ == "__main__":
    main()

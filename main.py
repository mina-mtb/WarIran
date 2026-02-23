import time
import os
from dotenv import load_dotenv
from engine.thermal_handler import ThermalHandler

def main():
    load_dotenv()
    print("--- WarIran Monitoring Engine ---")
    print("Status: Initializing components...")
    
    thermal_engine = ThermalHandler()
    
    # Placeholder for a user's target area (e.g., Tehran center)
    # In the future, this will come from the Database
    TARGET_LAT = 35.6892
    TARGET_LON = 51.3890
    RADIUS = 0.5 # approx 50km box for testing
    
    print(f"Status: Monitoring started for Coordinates ({TARGET_LAT}, {TARGET_LON})")
    
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running periodic check...")
        
        # 1. Check Thermal Anomalies (High Precision/Speed)
        hotspots = thermal_engine.fetch_recent_hotspots(range_days=1)
        if hotspots is not None:
            local_events = thermal_engine.filter_by_coordinates(
                hotspots, 
                TARGET_LAT - RADIUS, TARGET_LAT + RADIUS,
                TARGET_LON - RADIUS, TARGET_LON + RADIUS
            )
            
            if not local_events.empty:
                print(f"ALERT: Found {len(local_events)} thermal anomalies in the target area!")
                print(local_events[['latitude', 'longitude', 'acq_date', 'acq_time']])
                # TODO: Trigger Telegram Notification
            else:
                print("Status: No thermal anomalies detected in the target area.")
        
        # TODO: 2. Check SAR/Optical once data is fetched (Lower frequency)
        
        # Sleep for the interval defined in .env or default to 1 hour
        interval = int(os.getenv("CHECK_INTERVAL_SECONDS", 3600))
        time.sleep(interval)

if __name__ == "__main__":
    main()

import time
import os
from dotenv import load_dotenv
from engine.thermal_handler import ThermalHandler
from engine.gee_handler import GEEHandler
from utils.notifier import Notifier

def main():
    load_dotenv()
    print("--- WarIran Monitoring Engine ---")
    print("Status: Initializing components...")
    
    thermal_engine = ThermalHandler()
    gee_engine = GEEHandler()
    notifier = Notifier()
    
    # 1. Start-up Notification
    notifier.send_message("🚀 *WarIran Monitoring Engine started.* System is active.")
    
    if not gee_engine.authenticate():
        print("Warning: GEE authentication failed. Satellite verification will be disabled.")
    
    # 2. Get Monitoring Target from .env (Default: Isfahan)
    TARGET_LAT = float(os.getenv("MONITOR_LAT", 32.6546))
    TARGET_LON = float(os.getenv("MONITOR_LON", 51.6680))
    RADIUS = float(os.getenv("RADIUS_DEG", 0.5)) 
    
    print(f"Status: Monitoring started for Isfahan Region ({TARGET_LAT}, {TARGET_LON})")
    
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
                        
                        # Format alert for Telegram
                        alert_details = f"NASA FIRMS confidence: {event.get('confidence', 'N/A')}\n"
                        alert_details += f"SAR Change StdDev: {change_stats.get('VV_stdDev', 0):.4f}"
                        
                        notifier.send_alert("Thermal Anomaly + Structural Change Detected", e_lat, e_lon, details=alert_details)
            else:
                print("Status: No thermal anomalies detected.")
        
        # Sleep for the interval
        interval = int(os.getenv("CHECK_INTERVAL_SECONDS", 3600))
        time.sleep(interval)

if __name__ == "__main__":
    main()

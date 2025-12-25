import json
import time
import requests
import os
from datetime import datetime, timedelta

# --- Configuration ---
# Daejeon Yuseong-gu Guseong-dong (Grid X=67, Y=101)
GRID_X = 67
GRID_Y = 101
OUTPUT_FILE = "weather_data.json"

class WeatherFetcher:
    BASE_URL = "https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-dfs_shrt_grd"
    # Get key from Environment Variable for security
    AUTH_KEY = os.environ.get("KMA_API_KEY", "")
        
    @staticmethod
    def get_tmfc():
        now = datetime.now()
        # KMA Base Times: 02, 05, 08, 11, 14, 17, 20, 23
        base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
        candidates = []
        for h in base_hours:
            t = now.replace(hour=h, minute=0, second=0, microsecond=0)
            if t <= now:
                candidates.append(t)
        
        if not candidates:
            # If strictly before 02:00, use yesterday 23:00
            t = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
            candidates.append(t)
            
        return candidates[-1].strftime("%Y%m%d%H%M")

    @staticmethod
    def get_session():
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def fetch_data(tmfc, mode="2"):
        # mode=2 implies getting all variables? Usually we request specific vars or all.
        # Let's request specific vars for efficiency if supported, or rely on parsing.
        # Actually in common usage, we just fetch variables one by one or parsed from single big request if supported.
        # Simplest consistent way: Fetch common vars loop.
        
        vars_to_fetch = ["TMP", "SKY", "PTY", "WSD", "POP"]
        tmef_start = (datetime.now().replace(minute=0,second=0) + timedelta(hours=0)).strftime("%Y%m%d%H%M")
        
        # We need data for 04:00 ~ 08:00 TOMORROW (or Today if now is early morning?)
        # User wants "Early Morning Run". 
        # Logic: If it's currently afternoon/evening -> Show Tomorrow Morning.
        # If it's currently morning (before 9AM) -> Show Today Morning.
        
        now_hour = datetime.now().hour
        target_date = datetime.now()
        if now_hour >= 9: 
            target_date += timedelta(days=1) # Target Tomorrow
            
        target_times = []
        for h in range(4, 9): # 04, 05, 06, 07, 08
            t = target_date.replace(hour=h, minute=0, second=0, microsecond=0)
            target_times.append(t.strftime("%Y%m%d%H%M"))
        
        # We need to find the correct tmef strings relative to tmfc.
        # Just fetching by tmef is easiest if API supports specific tmef.
        
        session = WeatherFetcher.get_session()
        data_map = { t: {} for t in target_times }
        
        for var in vars_to_fetch:
            # We fetch a range or loop? Looping 5 times * 5 vars = 25 requests. Acceptable for backend.
            for tmef in target_times:
                url = f"{WeatherFetcher.BASE_URL}?tmfc={tmfc}&tmef={tmef}&vars={var}&authKey={WeatherFetcher.AUTH_KEY}"
                try:
                    resp = session.get(url, timeout=10)
                    resp.raise_for_status()
                    
                    # Parse
                    import re
                    tokens = re.split(r'[,\s]+', resp.text)
                    vals = [float(t) for t in tokens if t.strip() and not t.startswith('=')]
                    
                    # Grid index logic
                    # NX=149, NY=253. Total = 37697
                    # Index = Y * NX + X? Or X + Y * NX?
                    # Guideline: (y * NX) + x is standard row-major.
                    # HOWEVER, previous code had complex logic.
                    # Let's stick to the verified index logic or just use standard.
                    # Actually standard is usually flat array.
                    # Given fixed location, let's trust the logic from working app if available.
                    # But simpler: The app works with `values[-(NX*NY):]`.
                    # Index = (GRID_Y) * 149 + GRID_X
                    
                    idx = (GRID_Y * 149) + GRID_X
                    if len(vals) >= 149*253:
                         real_vals = vals[-(149*253):]
                         val = real_vals[idx]
                         data_map[tmef][var] = val
                except Exception as e:
                    print(f"Error fetching {var} at {tmef}: {e}")
                    pass
                time.sleep(0.2)
                
        return data_map

def main():
    print("Starting Weather Update...")
    tmfc = WeatherFetcher.get_tmfc()
    print(f"Base Time: {tmfc}")
    
    raw_data = WeatherFetcher.fetch_data(tmfc)
    
    # Transform to list for frontend
    # Expected: [{time: "04:00", temp: -5, ...}, ...]
    output_list = []
    
    # Sort keys to ensure order 04 -> 08
    for tmkey in sorted(raw_data.keys()):
        item = raw_data[tmkey]
        # Skip if incomplete
        if not item: continue
        
        # Format time "04:00"
        time_str = f"{tmkey[8:10]}:00"
        
        obj = {
            "time": time_str,
            "temp": item.get("TMP", -99),
            "sky": {1:"Sunny", 3:"Cloudy", 4:"Overcast"}.get(int(item.get("SKY", 0)), "Unknown"),
            "wind": item.get("WSD", 0),
            "pop": item.get("POP", 0),
            "pty": int(item.get("PTY", 0))
        }
        # Sky mapping fix for Clear vs Sunny consistency
        if obj['sky'] == "Sunny": obj['sky'] = "Clear"
        
        output_list.append(obj)
        
    # Valid check
    if not output_list:
        print("No Data Collected!")
        return # Don't overwrite with empty
        
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(output_list)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

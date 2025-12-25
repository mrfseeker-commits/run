import json
import time
import requests
import threading
import concurrent.futures
from datetime import datetime, timedelta
import sys

# --- Configuration ---
JSON_DB_PATH = "weather_code.json" # Relative path, assuming in same repo
LOCATIONS_TO_CHECK = [
    "서울특별시 강남구 역삼1동",
    "대전광역시 유성구 구성동",
    "부산광역시 해운대구 우제1동"
]

# --- 1. Weather Fetcher (Robust Backend Version) ---
class WeatherFetcher:
    BASE_URL = "https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-dfs_shrt_grd"
    AUTH_KEY = "JuUArlO6SrylAK5Tuoq8Ig"
    NX = 149
    NY = 253
    
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=3)
            cls._session.mount('https://', adapter)
            cls._session.mount('http://', adapter)
        return cls._session

    @staticmethod
    def get_tmfc():
        now = datetime.now()
        base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
        candidates = [now.replace(hour=h, minute=0, second=0, microsecond=0) for h in base_hours if now.replace(hour=h, minute=0, second=0, microsecond=0) <= now]
        if not candidates:
            t = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
            candidates.append(t)
        return candidates[-1].strftime("%Y%m%d%H%M")

    @staticmethod
    def get_tmef(tmfc):
        # Effective time logic
        dt = datetime.strptime(tmfc, "%Y%m%d%H%M")
        # Usually +4 hours from base time is a safe immediate forecast start, or just next hour
        # For simplicity, we stick to app logic or just current time simplified
        # App logic: current hour
        now = datetime.now()
        target = now.replace(minute=0, second=0, microsecond=0)
        return target.strftime("%Y%m%d%H%M")

    @staticmethod
    def fetch_grid_data(var, tmfc, tmef):
        url = f"{WeatherFetcher.BASE_URL}?tmfc={tmfc}&tmef={tmef}&vars={var}&authKey={WeatherFetcher.AUTH_KEY}"
        session = WeatherFetcher.get_session()
        
        for _ in range(5): # 5 retries
            try:
                resp = session.get(url, timeout=10)
                resp.raise_for_status()
                import re
                tokens = re.split(r'[,\s]+', resp.text)
                values = [float(t) for t in tokens if t.strip() and not t.startswith('=')]
                if len(values) >= WeatherFetcher.NX * WeatherFetcher.NY:
                   return values[-(WeatherFetcher.NX * WeatherFetcher.NY):]
            except:
                time.sleep(1.0)
                continue
        return None

    @staticmethod
    def get_timeseries(grid_x, grid_y, count=24): # Fetch 24 hours for backend report
        tmfc = WeatherFetcher.get_tmfc()
        base_tmef = WeatherFetcher.get_tmef(tmfc)
        
        timestamps = []
        dt_base = datetime.strptime(base_tmef, "%Y%m%d%H%M")
        for i in range(count):
            ts = (dt_base + timedelta(hours=i)).strftime("%Y%m%d%H%M")
            timestamps.append(ts)

        results_list = [{"tmef": ts, "_lock": threading.Lock()} for ts in timestamps]
        targets = ["TMP", "SKY", "PTY", "POP"] # Reduced targets for summary
        
        all_tasks = [(idx, t) for idx in range(count) for t in targets]
        
        def fetch_task(hour_idx, var_name):
            tmef = str(results_list[hour_idx]["tmef"])
            data = WeatherFetcher.fetch_grid_data(var_name, tmfc, tmef)
            if data:
                g_idx = grid_y * WeatherFetcher.NX + grid_x
                if 0 <= g_idx < len(data):
                    val = data[g_idx]
                    with results_list[hour_idx]["_lock"]:
                        results_list[hour_idx][var_name] = val

        # Conservative concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_task, idx, t) for idx, t in all_tasks]
            concurrent.futures.wait(futures)
            
        clean_results = []
        for r in results_list:
            d = r.copy()
            del d["_lock"]
            clean_results.append(d)
        return clean_results

# --- 2. Data Loader ---
def load_coords(json_path):
    import json
    import os
    if not os.path.exists(json_path):
        print(f"[ERROR] {json_path} not found.")
        return {}
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 3. Main Execution ---
def main():
    print(f"--- Weather Backend Report [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ---")
    
    # 1. Load Data
    coords_map = load_coords(JSON_DB_PATH)
    if not coords_map:
        sys.exit(1)
        
    # 2. Process Locations
    print(f"Target Locations: {LOCATIONS_TO_CHECK}")
    
    final_report = []
    
    for loc in LOCATIONS_TO_CHECK:
        if loc not in coords_map:
            print(f"[SKIP] Unknown location: {loc}")
            continue
            
        coord = coords_map[loc]
        gx, gy = coord['x'], coord['y']
        print(f"\n[FETCH] Processing {loc} (Grid: {gx}, {gy})...")
        
        data = WeatherFetcher.get_timeseries(gx, gy, count=6) # Get next 6 hours summary
        
        # Summarize first valid data point
        if data and data[0]:
            current = data[0]
            # Format report line
            sky_map = {1: "Sunny", 3: "Cloudy", 4: "Overcast"}
            pty_map = {0: "None", 1: "Rain", 2: "Rain/Snow", 3: "Snow", 4: "Shower"}
            
            tmp = current.get('TMP', '-')
            sky = sky_map.get(int(current.get('SKY', 0)), 'Unknown')
            pty = pty_map.get(int(current.get('PTY', 0)), '-')
            pop = current.get('POP', '-')
            
            summary = f"| {loc} | {current['tmef'][8:10]}:00 | {tmp}℃ | {sky} | {pty} | Rain Prob: {pop}% |"
            final_report.append(summary)
            print(f"   -> {tmp}℃, {sky}")
        else:
            final_report.append(f"| {loc} | Fetch Failed | - | - | - | - |")

    # 3. Output for GitHub Actions (Markdown)
    print("\n\n### :white_sun_small_cloud: Weather Report Summary")
    print("| Location | Time | Temp | Sky | Precip | POP |")
    print("| --- | --- | --- | --- | --- | --- |")
    for line in final_report:
        print(line)

if __name__ == "__main__":
    main()

import json
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# Daejeon Yuseong-gu Guseong-dong (Grid X=67, Y=101)
GRID_X = 67
GRID_Y = 101
OUTPUT_FILE = "weather_data.json"

def get_kst_now():
    """Returns current datetime in KST (UTC+9)."""
    return datetime.utcnow() + timedelta(hours=9)

class WeatherFetcher:
    """
    Fetches weather from Korea Open Data Portal (공공데이터포털).
    Uses VilageFcstInfoService_2.0 for much faster response.
    """
    BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    SERVICE_KEY = os.environ.get("DATA_GO_KR_API_KEY", "")
    
    @staticmethod
    def get_base_datetime():
        """
        Calculate the best base time for short-term forecast.
        For tomorrow morning (04:00-08:00) data, we need:
        - Use today's 0200 forecast (provides data up to +70 hours)
        - If before 02:10 today, use yesterday's 2300 forecast
        
        Base times: 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300
        """
        now = get_kst_now()
        
        # For GitHub Actions running hourly, we want stable base_time
        # that always includes 04:00-08:00 for tomorrow
        # Best option: use 0200 (if available) or 2300 from previous day
        
        if now.hour > 2 or (now.hour == 2 and now.minute >= 10):
            # After 02:10, use today's 0200 forecast
            base_dt = now.replace(hour=2, minute=0, second=0, microsecond=0)
        else:
            # Before 02:10, use yesterday's 2300 forecast
            yesterday = now - timedelta(days=1)
            base_dt = yesterday.replace(hour=23, minute=0, second=0, microsecond=0)
        
        return base_dt.strftime("%Y%m%d"), base_dt.strftime("%H%M")
    
    @staticmethod
    def fetch_forecast(nx, ny):
        """
        Fetch forecast data from public data portal.
        Returns parsed data for morning hours (04:00 - 08:00).
        """
        base_date, base_time = WeatherFetcher.get_base_datetime()
        
        params = {
            'serviceKey': WeatherFetcher.SERVICE_KEY,
            'numOfRows': 1000,
            'pageNo': 1,
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }
        
        try:
            resp = requests.get(WeatherFetcher.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Check for API errors
            header = data.get('response', {}).get('header', {})
            if header.get('resultCode') != '00':
                print(f"API Error: {header.get('resultMsg')}")
                return None
            
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            return items
            
        except Exception as e:
            print(f"Fetch error: {e}")
            return None


def parse_forecast_items(items):
    """
    Parse API response items into structured forecast data.
    Groups by fcstDate + fcstTime and extracts weather categories.
    """
    if not items:
        return []
    
    # Group items by forecast datetime
    forecast_map = {}
    
    for item in items:
        fcst_date = item.get('fcstDate', '')
        fcst_time = item.get('fcstTime', '')
        category = item.get('category', '')
        value = item.get('fcstValue', '')
        
        key = f"{fcst_date}{fcst_time}"
        if key not in forecast_map:
            forecast_map[key] = {'fcstDate': fcst_date, 'fcstTime': fcst_time}
        
        forecast_map[key][category] = value
    
    return forecast_map


def get_target_times():
    """
    Determine target morning hours (04:00 - 08:00).
    If after 7 AM, target tomorrow's morning.
    """
    now = get_kst_now()
    target_date = now
    
    if now.hour >= 7:
        target_date = now + timedelta(days=1)
    
    target_times = []
    for h in range(4, 9):  # 04, 05, 06, 07, 08
        t = target_date.replace(hour=h, minute=0, second=0, microsecond=0)
        target_times.append(t.strftime("%Y%m%d%H00"))
    
    return target_times


def main():
    print("Starting Weather Update (Public Data Portal API)...")
    
    # Fetch forecast
    items = WeatherFetcher.fetch_forecast(GRID_X, GRID_Y)
    
    if not items:
        print("Failed to fetch forecast data!")
        return
    
    print(f"Fetched {len(items)} forecast items")
    
    # Parse items
    forecast_map = parse_forecast_items(items)
    
    # Get target morning times
    target_times = get_target_times()
    print(f"Target times: {target_times}")
    
    # Extract data for target times
    output_list = []
    
    # Category mappings
    sky_map = {
        '1': 'Clear',
        '3': 'Cloudy', 
        '4': 'Overcast'
    }
    
    for target in target_times:
        fcst_date = target[:8]
        fcst_time = target[8:]
        key = f"{fcst_date}{fcst_time}"
        
        if key not in forecast_map:
            print(f"No data for {key}")
            continue
        
        data = forecast_map[key]
        
        # Parse values
        try:
            temp = float(data.get('TMP', -99))
        except:
            temp = -99
            
        try:
            wind = float(data.get('WSD', 0))
        except:
            wind = 0
            
        try:
            pop = int(data.get('POP', 0))
        except:
            pop = 0
            
        try:
            pty = int(data.get('PTY', 0))
        except:
            pty = 0
            
        sky_code = data.get('SKY', '1')
        sky = sky_map.get(sky_code, 'Unknown')
        
        obj = {
            "time": f"{fcst_time[:2]}:00",
            "temp": temp,
            "sky": sky,
            "wind": wind,
            "pop": pop,
            "pty": pty
        }
        
        output_list.append(obj)
    
    # Validate
    if not output_list:
        print("No data collected for target times!")
        return
    
    # Save to file
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(output_list)} items to {OUTPUT_FILE}")
    
    # Print summary
    for item in output_list:
        print(f"  {item['time']}: {item['temp']}°C, {item['sky']}, 강수확률 {item['pop']}%")


if __name__ == "__main__":
    main()

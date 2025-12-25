import tkinter as tk
from tkinter import ttk, messagebox
# import pandas as pd (removed for optimization)
import math
import requests
import os
import xml.etree.ElementTree as ET
import threading
import webbrowser

# --- 1. Coordinate Converter ---
class CoordinateConverter:
    """
    Converts Latitude/Longitude to KMA Grid (X, Y).
    Based on the official KMA conversion algorithm.
    """
    RE = 6371.00877  # Earth radius (km)
    GRID = 5.0       # Grid interval (km)
    SLAT1 = 30.0     # Projection latitude 1
    SLAT2 = 60.0     # Projection latitude 2
    OLON = 126.0     # Origin longitude
    OLAT = 38.0      # Origin latitude
    XO = 43          # Origin X (Grid)
    YO = 136         # Origin Y (Grid)

    @classmethod
    def to_grid(cls, lat, lon):
        degrad = math.pi / 180.0
        
        re = cls.RE / cls.GRID
        slat1 = cls.SLAT1 * degrad
        slat2 = cls.SLAT2 * degrad
        olon = cls.OLON * degrad
        olat = cls.OLAT * degrad

        sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
        sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
        sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
        sf = math.pow(sf, sn) * math.cos(slat1) / sn
        ro = math.tan(math.pi * 0.25 + olat * 0.5)
        ro = re * sf / math.pow(ro, sn)

        ra = math.tan(math.pi * 0.25 + lat * degrad * 0.5)
        ra = re * sf / math.pow(ra, sn)

        theta = lon * degrad - olon
        if theta > math.pi:
            theta -= 2.0 * math.pi
        if theta < -math.pi:
            theta += 2.0 * math.pi
        theta *= sn

        x = math.floor(ra * math.sin(theta) + cls.XO + 0.5)
        y = math.floor(ro - ra * math.cos(theta) + cls.YO + 0.5)
        
        return int(x), int(y)

# --- 2. Data Loader ---
# --- 2. Data Loader ---
# --- 2. Data Loader ---
class DataLoader:
    """
    Loads address and coordinate data.
    Uses optimized JSON file 'weather_code.json' for instant loading.
    """
    def __init__(self, json_path):
        self.json_path = json_path
        self.data_map = {}  # "Original Address String" -> {'x': ..., 'y': ...}
        self.search_keys = [] 

    def load_data(self):
        import time
        import json
        
        start_t = time.time()
        print(f"[DEBUG] Loading Data from Optimized JSON: {self.json_path}")
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data_map = json.load(f)
            
            self.search_keys = sorted(self.data_map.keys())
            elapsed = time.time() - start_t
            print(f"[DEBUG] Load Complete. Loaded {len(self.search_keys)} items in {elapsed:.4f}s.")
            return True, f"데이터 로딩 완료: {len(self.search_keys)}개 지역 ({elapsed:.2f}초)"
            
        except Exception as e:
            print(f"[DEBUG] Load Failed: {e}")
            return False, str(e)
# --- 3. Weather Fetcher (APIHub) ---
# --- 3. Weather Fetcher (APIHub) ---
class WeatherFetcher:
    """
    Fetches weather from KMA APIHub (nph-dfs_shrt_grd).
    Auth Key: Value from Env or Empty
    """
    BASE_URL = "https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-dfs_shrt_grd"
    AUTH_KEY = os.environ.get("KMA_API_KEY", "")
    
    # Grid dimensions
    NX = 149
    NY = 253

    @staticmethod
    def get_tmfc():
        """
        Calculate the most recent base time (02, 05, 08, 11, 14, 17, 20, 23).
        Returns string YYYYMMDDHHMM
        """
        from datetime import datetime, timedelta
        now = datetime.now()
        base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
        
        candidates = []
        for h in base_hours:
            t = now.replace(hour=h, minute=0, second=0, microsecond=0)
            if t <= now:
                candidates.append(t)
            else:
                pass
                
        if not candidates:
            # Must be early morning 00:00-01:59 -> use yesterday 23:00
            t = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
            candidates.append(t)
            
        latest = candidates[-1]
        return latest.strftime("%Y%m%d%H%M")

    @staticmethod
    def get_tmef(tmfc_str=None):
        # Effective time: Standard hourly alignment
        from datetime import datetime
        now = datetime.now()
        target = now.replace(minute=0, second=0, microsecond=0)
        return target.strftime("%Y%m%d%H%M")

    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            # Optional: efficient connection pooling
            adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=3)
            cls._session.mount('https://', adapter)
            cls._session.mount('http://', adapter)
        return cls._session

    @staticmethod
    def fetch_grid_data(var, tmfc, tmef):
        """
        Fetches the grid for a single variable.
        Returns a flat list of values.
        """
        url = f"{WeatherFetcher.BASE_URL}?tmfc={tmfc}&tmef={tmef}&vars={var}&authKey={WeatherFetcher.AUTH_KEY}"
        
        import time
        max_retries = 5
        session = WeatherFetcher.get_session()
        
        for attempt in range(max_retries):
            try:
                # 10s timeout, use session for Keep-Alive
                resp = session.get(url, timeout=10)
                resp.raise_for_status()
                
                # The format is a header lines followed by space/comma separated values.
                import re
                tokens = re.split(r'[,\s]+', resp.text)
                values = [float(t) for t in tokens if t.strip() and not t.startswith('=')]
                
                if len(values) >= WeatherFetcher.NX * WeatherFetcher.NY:
                   return values[-(WeatherFetcher.NX * WeatherFetcher.NY):]
                # If short, retry
            except Exception as e:
                time.sleep(1.0) # Longer wait (1s)
                continue
                
        # If all retries failed
        print(f"[FERR] Fetch failed for {var} at {tmef} after {max_retries} attempts.")
        return None

    @staticmethod
    def add_hours(tmstr, hours):
        from datetime import datetime, timedelta
        dt = datetime.strptime(tmstr, "%Y%m%d%H%M")
        target = dt + timedelta(hours=hours)
        return target.strftime("%Y%m%d%H%M")

    @staticmethod
    def get_timeseries(grid_x, grid_y, count=36, progress_cb=None):
        tmfc = WeatherFetcher.get_tmfc()
        
        # Determine timestamps
        timestamps = []
        for i in range(count):
             base_tmef = WeatherFetcher.get_tmef(tmfc) 
             ts = WeatherFetcher.add_hours(base_tmef, i)
             timestamps.append(ts)

        # Pre-allocate results with thread-safe locks
        results_list = [{"tmef": ts, "_lock": threading.Lock()} for ts in timestamps]
        
        targets = ["TMP", "SKY", "PTY", "WSD", "PCP", "SNO", "REH", "POP"]
        
        # Flatten tasks: (hour_index, variable)
        all_tasks = []
        for idx in range(count):
            for t in targets:
                all_tasks.append((idx, t))
        
        total_tasks = len(all_tasks)
        completed = 0
        main_lock = threading.Lock() # for progress counter
        
        def fetch_task(hour_idx, var_name):
            nonlocal completed
            tmef = str(results_list[hour_idx]["tmef"])
            
            # Fetch
            data = WeatherFetcher.fetch_grid_data(var_name, tmfc, tmef)
            
            # Update result
            if data:
                # Calc grid index
                # Data is likely Bottom-Up (Index 0 is South, Last is North)
                # Previous formula assumed Top-Down (NY-1-y), which fetched Northern (colder) data.
                g_idx = grid_y * WeatherFetcher.NX + grid_x
                
                val = None
                if 0 <= g_idx < len(data):
                    val = data[g_idx]
                
                # Update shared dict with specific lock
                with results_list[hour_idx]["_lock"]:
                    results_list[hour_idx][var_name] = val
                    
            # Progress update
            with main_lock:
                completed += 1
                if progress_cb and completed % 5 == 0: # Update every 5 to reduce UI spam
                    progress_cb(completed, total_tasks, f"데이터 수신 중... ({int(completed/total_tasks*100)}%)")

        import concurrent.futures
        # Very Conservative Parallelism
        # 4 workers avoids KMA blocking/throttling.
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(fetch_task, idx, t) for idx, t in all_tasks]
            concurrent.futures.wait(futures)
            
        # Clean up locks from results
        clean_results = []
        for r in results_list:
            d = r.copy()
            del d["_lock"]
            clean_results.append(d)
            
        return clean_results

# --- 4. GUI Application ---
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("전국 동네예보 검색 (KMA Weather)")
        self.root.geometry("800x1000") 
        
        self.recents = []
        self.load_recents()
        
        # UI Elements
        self.setup_ui()
        
        self.fetcher = WeatherFetcher()
        
        # Initialize Logic
        # Data Loader (Optimized JSON)
        json_path = r"C:\Users\강호건\Documents\cursor\openweather\weather_code.json"
        
        self.loader = DataLoader(json_path)
        
        # Initial data loading
        self.output_log("주소 데이터를 로딩중입니다...")
        self.root.update() # Force UI update to show loading status
        
        success, msg = self.loader.load_data()
        self.output_log(msg)

    def load_recents(self):
        import json
        import os
        try:
            if os.path.exists("recents.json"):
                with open("recents.json", "r", encoding="utf-8") as f:
                    self.recents = json.load(f)
        except:
            self.recents = []

    def save_recents(self):
        import json
        try:
            with open("recents.json", "w", encoding="utf-8") as f:
                json.dump(self.recents, f, ensure_ascii=False)
        except:
            pass

    def setup_ui(self):
        # 1. Search Frame
        search_frame = tk.Frame(self.root, pady=5)
        search_frame.pack(fill='x', padx=10)
        
        tk.Label(search_frame, text="주소 검색:").pack(side='left')
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', self.on_enter)
        self.search_entry.bind('<Down>', self.on_arrow_down)
        
        btn_search = tk.Button(search_frame, text="날씨 조회", command=self.fetch_weather_btn)
        btn_search.pack(side='left')

        # 1-1. Recents Frame
        self.recents_frame = tk.Frame(self.root, pady=5)
        self.recents_frame.pack(fill='x', padx=10)
        tk.Label(self.recents_frame, text="최근 검색:").pack(side='left')
        self.recent_buttons_frame = tk.Frame(self.recents_frame)
        self.recent_buttons_frame.pack(side='left', padx=5)
        self.update_recents_ui()

        # 2. Listbox for Autocomplete
        self.listbox_frame = tk.Frame(self.root)
        self.listbox_frame.pack(fill='x', padx=10)
        
        self.listbox = tk.Listbox(self.listbox_frame, height=5)
        self.listbox.pack(fill='x')
        self.listbox.bind('<<ListboxSelect>>', self.on_list_select)
        self.listbox.bind('<Return>', self.on_list_confirm)
        self.listbox.bind('<ButtonRelease-1>', self.on_list_confirm)
        self.listbox_frame.pack_forget() 

        # 3. Result Area
        result_frame = tk.LabelFrame(self.root, text="상세 날씨 (시계열)", padx=10, pady=10)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.location_label = tk.Label(result_frame, text="주소: -", font=("Malgun Gothic", 11, "bold"))
        self.location_label.pack(anchor='w', pady=(0, 10))

        # Progress Bar Frame (Normally hidden or 0)
        self.prog_frame = tk.Frame(result_frame)
        self.prog_frame.pack(fill='x', padx=5, pady=5)
        self.progress = ttk.Progressbar(self.prog_frame, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill='x')
        self.prog_label = tk.Label(self.prog_frame, text="대기중...")
        self.prog_label.pack(side='bottom')
        self.prog_frame.pack_forget()

        # Treeview
        cols = ("시간", "기온", "하늘", "강수형태", "강수확률", "습도", "풍속", "강수량", "적설")
        self.tree = ttk.Treeview(result_frame, columns=cols, show='headings', height=38)
        
        widths = [120, 60, 80, 80, 70, 60, 120, 100, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor='center')
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 4. Status Bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')

    def update_prog(self, cur, total, msg):
        # Thread-safe update
        def _update():
            self.progress['maximum'] = total
            self.progress['value'] = cur
            self.prog_label.config(text=f"{msg} ({cur}/{total})")
        self.root.after(0, _update)

    def output_log(self, msg):
        self.status_var.set(msg)

    # ... (Load, Search, Recents same) ...
    def load_data_thread(self):
        success, msg = self.loader.load_data()
        self.root.after(0, lambda: self.output_log(msg))

    def update_recents_ui(self):
        for widget in self.recent_buttons_frame.winfo_children():
            widget.destroy()
        for addr in self.recents:
            def make_cmd(a):
                return lambda: self.request_fetch(a, confirm=True) 
            btn = tk.Button(self.recent_buttons_frame, text=addr, command=make_cmd(addr), font=("Malgun Gothic", 9))
            btn.pack(side='left', padx=2)

    def on_search_change(self, *args):
        if getattr(self, 'ignore_search_change', False):
            return
            
        typed = self.search_var.get()
        if not typed:
            self.listbox_frame.pack_forget()
            return
        matches = [k for k in self.loader.search_keys if typed in k][:50]
        if matches:
            self.listbox.delete(0, tk.END)
            for m in matches:
                self.listbox.insert(tk.END, m)
            self.listbox_frame.pack(fill='x', padx=10, before=self.location_label.master) 
        else:
            self.listbox_frame.pack_forget()

    def on_list_select(self, event):
        # Just update the text box, do not fetch yet
        if not self.listbox.curselection(): return
        selection = self.listbox.get(self.listbox.curselection())
        
        self.ignore_search_change = True
        self.search_var.set(selection)
        self.ignore_search_change = False

    def on_list_confirm(self, event):
        # Triggered by Enter or Click
        if not self.listbox.curselection(): return
        selection = self.listbox.get(self.listbox.curselection())
        
        self.ignore_search_change = True
        self.search_var.set(selection)
        self.ignore_search_change = False
        
        self.listbox_frame.pack_forget()
        self.request_fetch(selection, confirm=True)

    def on_enter(self, event):
        if self.listbox_frame.winfo_ismapped() and self.listbox.size() > 0:
            # If list is open and user hits enter, check if something is selected?
            # Or just default to first item if nothing selected?
            # Or just fetch what is in the box?
            # Let's say Enter in entry box -> Just fetch what is in box (which matches logic)
            # But if list is focused? on_enter is bound to Entry.
            pass
        self.fetch_weather_btn()

    def on_arrow_down(self, event):
        if self.listbox_frame.winfo_ismapped():
            self.listbox.focus_set()
            self.listbox.selection_set(0)

    def fetch_weather_btn(self):
        addr = self.search_var.get()
        self.request_fetch(addr, confirm=True)

    def request_fetch(self, addr, confirm=True):
        if not addr: return
        self.fetch_weather_action(addr)

    def fetch_weather_action(self, addr):
        if addr not in self.loader.data_map:
            messagebox.showerror("오류", "리스트에 없는 주소입니다.\n검색어를 확인해주세요.")
            return
            
        # Add to recents
        if addr in self.recents:
            self.recents.remove(addr)
        self.recents.insert(0, addr)
        if len(self.recents) > 5:
            self.recents = self.recents[:5]
        self.save_recents()
        self.update_recents_ui()
            
        data = self.loader.data_map[addr]
        # Direct X, Y from official file
        gx, gy = data['x'], data['y']
        
        self.location_label.config(text=f"주소: {addr} (X:{gx}, Y:{gy})")
        self.output_log("조회 시작...")
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Show progress
        self.prog_frame.pack(fill='x', padx=5, pady=5, before=self.tree)
        self.progress['value'] = 0
            
        threading.Thread(target=self.do_fetch, args=(gx, gy)).start()

    def do_fetch(self, gx, gy):
        # Fetch 36 hours with callback
        data_list = self.fetcher.get_timeseries(gx, gy, count=36, progress_cb=self.update_prog)
        
        self.root.after(0, lambda: self.fill_tree(data_list))

    def fill_tree(self, data_list):
        self.prog_frame.pack_forget() # Hide progress
        
        if not data_list:
            self.output_log("데이터 조회 실패")
            return

        cnt = 0
        def safe_int(val, default=0):
            if val is None: return default
            try: return int(val)
            except: return default
            
        sky_map = {1: "맑음", 3: "구름많음", 4: "흐림"}
        pty_map = {0: "없음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기"}

        for row in data_list:
            if not row: continue
            
            t_str = row.get("tmef", "")
            if len(t_str) == 12:
                time_disp = f"{t_str[4:6]}/{t_str[6:8]} {t_str[8:10]}:{t_str[10:12]}"
            else:
                time_disp = t_str
                
            tmp = row.get("TMP")
            # Robust missing check: None, -50, or -99 (often API missing)
            if tmp is None or tmp <= -50 or tmp == -99.0: tmp = "-"
            
            sky_val = safe_int(row.get("SKY"), 0)
            sky = sky_map.get(sky_val, "-")
            
            pty_val = safe_int(row.get("PTY"), 0)
            pty = pty_map.get(pty_val, "-")
            
            pop = row.get("POP", "-")
            if pop == -1 or pop == -99.0: pop = "-"
            
            reh = row.get("REH", "-")
            if reh == -1 or reh == -99.0: reh = "-"
            
            wsd = row.get("WSD", 0)
            if wsd == -1 or wsd is None or wsd == -99.0: wsd = 0
            
            wsd_desc = ""
            if wsd >= 9: wsd_desc = "(강)"
            elif wsd >= 4: wsd_desc = "(약강)"
            
            wsd_str = f"{wsd} {wsd_desc}" if wsd_desc else f"{wsd}"
            
            pcp = safe_int(row.get("PCP"), 0)
            sno = safe_int(row.get("SNO"), 0)
            
            pcp_str = "-"
            if pcp == 1: pcp_str = "<3mm"
            elif pcp == 2: pcp_str = "3-15mm"
            elif pcp >= 3: pcp_str = "15mm+"
            elif pcp == -99: pcp_str = "-"
            
            sno_str = "-"
            if sno == 1: sno_str = "<1cm"
            elif sno >= 2: sno_str = "1cm+"
            elif sno == -99: sno_str = "-"

            self.tree.insert("", "end", values=(
                time_disp,
                f"{tmp} ℃" if tmp != "-" else "-",
                sky,
                pty,
                f"{pop} %" if pop != "-" else "-",
                f"{reh} %" if reh != "-" else "-",
                wsd_str,
                pcp_str,
                sno_str
            ))
            cnt += 1
            
        self.output_log(f"조회 완료 ({cnt}개 시간대)")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

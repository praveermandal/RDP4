import os
import time
import re
import random
import datetime
import threading
import sys
import gc
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

# 📦 SELENIUM & DRIVER TOOLS
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- V102 TUNED CONFIGURATION ---
THREADS = 2             # 2 Browsers
TABS_PER_AGENT = 3      # 3 Tabs per Browser (Total 6 Streams)
TOTAL_DURATION = 25000  

# ⚡ TARGET SPEED
BURST_MIN = 0.05        # Dropped to 50ms for maximum fire
BURST_MAX = 0.08

# ♻️ RESTART CYCLES
SESSION_MAX_SEC = 120    

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    with BROWSER_LAUNCH_LOCK:
        time.sleep(1) 
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"v102_{agent_id}_{int(time.time())}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux armv8l", 
            webgl_vendor="ARM",
            renderer="Mali-G76",
            fix_hairline=True,
        )
        return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[@contenteditable='true']"]
    for xpath in selectors:
        try: return driver.find_element(By.XPATH, xpath)
        except: continue
    return None

def adaptive_inject(driver, element, text):
    try:
        driver.execute_script("arguments[0].focus();", element)
        driver.execute_script("document.execCommand('insertText', false, arguments[0]);", text)
        element.send_keys(Keys.ENTER)
        return True
    except: return False

def get_dynamic_block(target_name):
    emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"]
    selected_emoji = random.choice(emojis)
    base_underlines = 24
    adjustment = len(target_name) - 4 
    num_underlines = max(5, base_underlines - adjustment)
    underlines = "_" * num_underlines
    line = f"【 {target_name} 】 SAY P R V R बाप {selected_emoji} {underlines}/"
    block = "\n".join([line for _ in range(20)])
    return f"{block}\n⚡ ID: {random.randint(1000, 9999)}"

def tab_striker(driver, handle, agent_id, target_name, session_start, global_start):
    """Internal loop for each tab to fire independently."""
    driver.switch_to.window(handle)
    msg_box = find_mobile_box(driver)
    
    while (time.time() - session_start) < SESSION_MAX_SEC:
        if (time.time() - global_start) > TOTAL_DURATION: break
        if msg_box:
            final_text = get_dynamic_block(target_name)
            adaptive_inject(driver, msg_box, final_text)
        time.sleep(random.uniform(BURST_MIN, BURST_MAX))

def run_life_cycle(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        try:
            log_status(agent_id, "🚀 Launching Multi-Stream Browser...")
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # --- PARALLEL TAB LAUNCH ---
            for _ in range(TABS_PER_AGENT):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(3) # Ultra-fast stagger

            handles = driver.window_handles[1:]
            
            # Use ThreadPool to fire from all tabs at the same time
            with ThreadPoolExecutor(max_workers=TABS_PER_AGENT) as tab_executor:
                for h in handles:
                    tab_executor.submit(tab_striker, driver, h, agent_id, target_name, session_start, global_start)
                
        except Exception as e:
            log_status(agent_id, f"⚠️ Error: {e}")
        finally:
            log_status(agent_id, "♻️ RAM Flush & Reboot")
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA") 
    
    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

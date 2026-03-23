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

# --- V102.5 TUNED CONFIGURATION ---
TABS_PER_AGENT = 3      # 3 Threads firing on 3 tabs simultaneously
TOTAL_DURATION = 25000  

# ⚡ TARGET SPEED (Ultra-Low Python Latency)
BURST_MIN = 0.01 
BURST_MAX = 0.03

# ♻️ RESTART CYCLES
SESSION_MAX_SEC = 120    

sys.stdout.reconfigure(encoding='utf-8')
COUNTER_LOCK = threading.Lock()
GLOBAL_SENT = 0

def log_status(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [Phoenix]: {msg}", flush=True)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v102_hybrid_{int(time.time())}")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[@contenteditable='true']"]
    for xpath in selectors:
        try: return driver.find_element(By.XPATH, xpath)
        except: continue
    return None

def adaptive_inject(driver, element, text):
    try:
        # 🚀 Using your working "Command-Insert" logic
        driver.execute_script("arguments[0].focus();", element)
        driver.execute_script("document.execCommand('insertText', false, arguments[0]);", text)
        element.send_keys(Keys.ENTER)
        return True
    except: return False

def get_dynamic_block(target_name):
    emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"]
    line = f"【 {target_name} 】 SAY P R V R बाप {random.choice(emojis)} ________________________/"
    block = "\n".join([line for _ in range(20)])
    return f"{block}\n⚡ ID: {random.randint(1000, 9999)}"

def tab_worker(driver, handle, target_name, session_start):
    """Independent Python thread for each tab."""
    try:
        driver.switch_to.window(handle)
        time.sleep(2)
        msg_box = find_mobile_box(driver)
        
        while (time.time() - session_start) < SESSION_MAX_SEC:
            final_text = get_dynamic_block(target_name)
            if adaptive_inject(driver, msg_box, final_text):
                with COUNTER_LOCK:
                    global GLOBAL_SENT
                    GLOBAL_SENT += 1
            time.sleep(random.uniform(BURST_MIN, BURST_MAX))
    except: pass

def main_cycle():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA")
    
    global_start = time.time()
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        try:
            log_status("🚀 Launching Hybrid Engine...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Open 3 Tabs quickly
            for _ in range(TABS_PER_AGENT):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(3)

            handles = driver.window_handles[1:]
            
            # 🔥 Start 3 parallel Python threads on the same browser
            threads = []
            for h in handles:
                t = threading.Thread(target=tab_worker, args=(driver, h, target_name, session_start))
                t.start()
                threads.append(t)

            # Wait for 2-minute cycle to end
            time.sleep(SESSION_MAX_SEC)
                
        except Exception as e:
            log_status(f"⚠️ Error: {e}")
        finally:
            log_status("♻️ Nuclear Purge & RAM Reset")
            if driver: driver.quit()
            gc.collect()

if __name__ == "__main__":
    main_cycle()

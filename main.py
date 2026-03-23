import os
import time
import re
import random
import datetime
import threading
import sys
import gc
import tempfile
import subprocess
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

# --- V100 TUNED CONFIGURATION ---
THREADS = 2             # 2 Agents per machine (10 Agents Total)
TOTAL_DURATION = 25000  # ~7 Hours

# ⚡ TARGET SPEED: 80ms - 100ms
BURST_MIN = 0.08
BURST_MAX = 0.10

# ♻️ RESTART CYCLES (2 Minutes)
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
        time.sleep(2) 
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
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"v100_{agent_id}_{int(time.time())}")
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
        driver.custom_temp_path = temp_dir
        return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[@contenteditable='true']"]
    for xpath in selectors:
        try: 
            return driver.find_element(By.XPATH, xpath)
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
    """Generates a fresh 20-line block with a rotating emoji and auto-aligned underlines."""
    emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"]
    selected_emoji = random.choice(emojis)
    
    # Target length for the underline section to maintain alignment
    # If the name gets longer, we subtract underlines to keep the total width same
    base_underlines = 24
    adjustment = len(target_name) - 4 # 4 is the length of 'EZRA'
    num_underlines = max(5, base_underlines - adjustment)
    underlines = "_" * num_underlines

    # The perfect format you requested
    line = f"【 {target_name} 】 SAY P R V R बाप {selected_emoji} {underlines}/"
    
    # Build the 20-line block
    block = "\n".join([line for _ in range(20)])
    # Unique ID to bypass duplicate filters
    return f"{block}\n⚡ ID: {random.randint(1000, 9999)}"

def run_life_cycle(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        try:
            log_status(agent_id, "🚀 Launching Browser...")
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(5)

            msg_box = find_mobile_box(driver)
            
            # --- THE FIRING LOOP ---
            while (time.time() - session_start) < SESSION_MAX_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break
                
                # 🔄 Generates fresh block with a new emoji each time
                final_text = get_dynamic_block(target_name)
                
                if adaptive_inject(driver, msg_box, final_text):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                
                # ⚡ Burst Pulse Delay
                time.sleep(random.uniform(BURST_MIN, BURST_MAX))
                
        except Exception as e:
            log_status(agent_id, f"⚠️ Error: {e}")
        finally:
            log_status(agent_id, "♻️ 2-Minute Restart & RAM Flush")
            if driver: driver.quit()
            gc.collect()

def main():
    # 🔑 Credentials from GitHub Secrets
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA") # Defaults to EZRA if secret is missing
    
    if not cookie or not target_id:
        print("❌ Missing Secrets (INSTA_COOKIE or TARGET_THREAD_ID)!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

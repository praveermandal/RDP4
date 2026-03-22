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

def run_life_cycle(agent_id, cookie, target, messages):
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
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)

            msg_box = find_mobile_box(driver)
            
            # --- THE FIRING LOOP ---
            while (time.time() - session_start) < SESSION_MAX_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break
                
                msg = random.choice(messages)
                if adaptive_inject(driver, msg_box, f"{msg} {random.randint(10,99)}"):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                
                # ⚡ 80ms - 100ms Pulse
                time.sleep(random.uniform(BURST_MIN, BURST_MAX))
        except: pass
        finally:
            log_status(agent_id, "♻️ 2-Minute Restart & RAM Flush")
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target = os.environ.get("TARGET_THREAD_ID", "")
    messages = os.environ.get("MESSAGES", "Strike").split("|")
    
    if not cookie or not target:
        print("❌ Missing Secrets!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()

import os
import time
import re
import random
import datetime
import threading
import sys
import gc
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- V81 CONFIGURATION ---
THREADS = 1             # 👤 Single Agent
TOTAL_DURATION = 21600  # 6 Hours

# ⚡ BURST SETTINGS
BURST_RANGE = (10, 20)      # Send 10-20 messages...
REST_RANGE = (10, 20)       # ...then sleep 10-20 seconds.
BURST_SPEED = (0.5, 1.2)    # Typing speed

# 🔄 RESTART SETTINGS
# The browser will be KILLED and REOPENED every 3 to 5 minutes.
SESSION_MIN_SEC = 180       # 3 Minutes
SESSION_MAX_SEC = 300       # 5 Minutes

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🤖 Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # ❌ REMOVED ECO-MODE FLAGS (Standard Browser)
    # The browser will now behave normally, caching files as needed.
    
    # Block Images (Still good for speed)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Stealth
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Mobile Emulation
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v81_{agent_id}_{random.randint(100,999)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[@contenteditable='true']"]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            if el.is_displayed(): return el
        except: continue
    return None

def adaptive_inject(driver, element, text):
    try:
        element.click()
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, text)
        
        time.sleep(0.1)
        
        try:
            btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
            btn.click()
        except:
            element.send_keys(Keys.ENTER)
        return True
    except:
        return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    global_start = time.time()

    # 🔄 OUTER LOOP: Runs for 6 Hours
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        
        # Determine how long this browser lives (3-5 mins)
        current_session_limit = random.randint(SESSION_MIN_SEC, SESSION_MAX_SEC)
        session_start = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Standard Browser...")
            driver = get_driver(agent_id)
            
            driver.get("https://www.instagram.com/")
            WebDriverWait(driver, 20).until(lambda d: "instagram.com" in d.current_url)

            clean_session = extract_session_id(cookie)
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/', 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(4) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)
            
            log_status(agent_id, "✅ Connected. Starting Burst.")
            msg_box = find_mobile_box(driver)

            # ⚡ BURST TRACKERS
            current_burst_count = 0
            current_burst_limit = random.randint(*BURST_RANGE)

            # ♻️ SESSION LOOP (Runs for 3-5 Mins)
            while (time.time() - session_start) < current_session_limit:
                if (time.time() - global_start) > TOTAL_DURATION: break

                if not msg_box:
                    msg_box = find_mobile_box(driver)
                    if not msg_box:
                        time.sleep(5)
                        continue

                # --- BURST LOGIC ---
                if current_burst_count >= current_burst_limit:
                    rest_time = random.randint(*REST_RANGE)
                    log_status(agent_id, f"💤 Resting {rest_time}s...")
                    time.sleep(rest_time)
                    
                    # Reset
                    current_burst_count = 0
                    current_burst_limit = random.randint(*BURST_RANGE)
                # -------------------

                msg = random.choice(messages)
                if adaptive_inject(driver, msg_box, f"{msg} "):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                    current_burst_count += 1
                    
                    # 🔒 CLEAN LOGS
                    log_status(agent_id, "✅ Sent message")
                
                # Burst Speed
                wait_time = random.uniform(*BURST_SPEED)
                time.sleep(wait_time)

        except Exception as e:
            log_status(agent_id, "⚠️ Browser Glitch. Killing...")
        
        finally:
            log_status(agent_id, "💀 Killing Browser (Refresh Cycle).")
            if driver: 
                try: driver.quit()
                except: pass
            
            gc.collect() 
            time.sleep(3) # Short pause before re-opening

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")
    
    if not cookie: sys.exit(1)

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()

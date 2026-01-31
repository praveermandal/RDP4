import os
import time
import re
import random
import datetime
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# --- V65 MARATHON CONFIGURATION ---
THREADS = 1             
BASE_SPEED = 0.5        

# ⏱️ LONG HAUL SETTINGS
# We stop at 5h 55m (21300s) to exit gracefully before GitHub force-kills us.
TOTAL_DURATION = 21300  

# ♻️ PERFORMANCE CYCLE 
# Restart Browser every 40 mins to keep it fast and prevent RAM crashes.
BROWSER_LIFESPAN = 2400 

# 💤 SAFETY DELAY
# Wait 2 minutes between sessions or after a crash.
RESTART_DELAY = 120     

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
    
    # Block Images for speed
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Anti-Detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Mobile Emulation (Pixel 5)
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
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
        # JavaScript Injection for reliability
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, text)
        time.sleep(0.1)
        
        # Try finding the Send button
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
    global_start_time = time.time()
    
    # ♾️ THE INVINCIBLE LOOP
    while True:
        # 1. Check if the 6-hour shift is over
        if (time.time() - global_start_time) > TOTAL_DURATION:
            log_status(agent_id, "✅ Shift Complete (5h 55m). Exiting for scheduled restart.")
            break

        driver = None
        browser_start_time = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Fresh Browser...")
            driver = get_driver(agent_id)
            
            # --- CONNECTION ---
            driver.get("https://www.instagram.com/")
            WebDriverWait(driver, 20).until(lambda d: "instagram" in d.current_url)
            
            clean_session = extract_session_id(cookie)
            # Using specific domain strategy for Mobile
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/', 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(5) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(8)
            log_status(agent_id, "✅ Connected. Running Performance Cycle.")

            # --- MESSAGING LOOP (Stops after 40 mins) ---
            while (time.time() - browser_start_time) < BROWSER_LIFESPAN:
                # Double check global limit inside the loop
                if (time.time() - global_start_time) > TOTAL_DURATION: break

                msg_box = find_mobile_box(driver)
                if msg_box:
                    msg = random.choice(messages)
                    if adaptive_inject(driver, msg_box, f"{msg} "):
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        log_status(agent_id, f"Sent: {msg}")
                
                time.sleep(BASE_SPEED)

        except Exception as e:
            # 🛡️ CATCH ALL CRASHES
            log_status(agent_id, f"⚠️ Crash Detected: {e}")
            log_status(agent_id, "🔄 Rebooting browser in 2 minutes...")
        
        finally:
            # 🗑️ CLEANUP
            if driver: 
                try: driver.quit()
                except: pass
            
            # 💤 2 MINUTE WAIT (Before next attempt)
            # This happens after a crash OR after a successful 40-min run.
            time.sleep(RESTART_DELAY)

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

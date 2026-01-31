import os
import time
import re
import random
import datetime
import sys
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# --- V65 CONFIGURATION ---
THREADS = 1             # Keep at 1 for safety
BASE_BURST = 5          
BASE_SPEED = 0.5        

# ⏱️ TIME SETTINGS
# GitHub Actions Limit is 6 Hours (21600s). We set 21000s to be safe.
TOTAL_DURATION = 21000  

# ♻️ GARBAGE COLLECTION
# Restart Browser every 30 mins (1800s) to prevent RAM crashes
BROWSER_LIFESPAN = 1800 

GLOBAL_SENT = 0

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🤖 Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Block Images (Speed + RAM Saver)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Anti-Detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Mobile Emulation
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_v65_{agent_id}_{random.randint(100,999)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def adaptive_inject(driver, element, text):
    try:
        element.click()
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, text)
        time.sleep(0.1)
        try:
            driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']").click()
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
    
    # 🔄 THE INFINITE LOOP (Up to 6 hours)
    while (time.time() - global_start_time) < TOTAL_DURATION:
        driver = None
        browser_start_time = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Fresh Browser (Cycle Start)...")
            driver = get_driver(agent_id)
            
            # Connection Retry Logic
            connected = False
            for attempt in range(3):
                try:
                    driver.get("https://www.instagram.com/")
                    WebDriverWait(driver, 10).until(lambda d: "instagram.com" in d.current_url)
                    connected = True
                    break
                except:
                    time.sleep(2)
            
            if not connected:
                raise Exception("Network Failure")

            # Login
            clean_session = extract_session_id(cookie)
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/', 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(4) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(6)
            
            log_status(agent_id, "✅ Connected. Loop Started.")

            # ⚡ SHORT LOOP (30 Mins max per browser)
            while (time.time() - browser_start_time) < BROWSER_LIFESPAN:
                # Double check global time
                if (time.time() - global_start_time) > TOTAL_DURATION:
                    break

                try:
                    msg_box = driver.find_element(By.XPATH, "//textarea | //div[@role='textbox'] | //div[@contenteditable='true']")
                except:
                    time.sleep(5)
                    continue

                msg = random.choice(messages)
                if adaptive_inject(driver, msg_box, f"{msg} "):
                    log_status(agent_id, f"Sent: {msg}")
                
                time.sleep(BASE_SPEED)

        except Exception as e:
            log_status(agent_id, f"❌ Error: {e}")
            time.sleep(10) # Wait before retry
        
        finally:
            # 🗑️ KILL BROWSER (Garbage Collection)
            if driver: 
                log_status(agent_id, "♻️ Recycling Browser (Clearing RAM)...")
                try: driver.quit()
                except: pass
            
            # Short break between cycles
            time.sleep(5)

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

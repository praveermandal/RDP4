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

# --- V69 CONFIGURATION ---
THREADS = 2             
BASE_SPEED = 0.5        

# ⏱️ LONG HAUL SETTINGS
TOTAL_DURATION = 21300  
BROWSER_LIFESPAN = 2400 
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
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    mobile_emulation = {
        "deviceMetrics": { "width": 393, "height": 851, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_agent_{agent_id}_{random.randint(1000,9999)}")
    
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
        
        # 🛠️ THE GHOST FIX 🛠️
        # 1. Wake up the box with a real keypress
        element.send_keys(" ") 
        time.sleep(0.1)
        
        # 2. Inject the text safely
        driver.execute_script("""
            var el = arguments[0];
            el.value = arguments[1];
            el.innerText = arguments[1];
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, text)
        time.sleep(0.1)
        
        # 3. Trigger one more update to turn the button BLUE
        element.send_keys(" ") 
        time.sleep(0.3) # Wait for button to activate
        
        # 4. Hunt for the Send Button
        send_xpaths = [
            "//div[text()='Send']",
            "//button[text()='Send']",
            "//div[contains(@class, 'xjqpnuy')]" # Obfuscated class
        ]
        
        clicked = False
        for xpath in send_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                # Check if it's visible and clickable
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    break
            except:
                continue
        
        # Fallback: Enter Key
        if not clicked:
            element.send_keys(Keys.ENTER)
            
        return True
    except:
        return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    # 🛑 STAGGER START (Prevents Crash)
    startup_delay = (agent_id - 1) * 20
    if startup_delay > 0:
        log_status(agent_id, f"💤 Waiting {startup_delay}s to stagger launch...")
        time.sleep(startup_delay)

    global_start_time = time.time()
    
    while True:
        if (time.time() - global_start_time) > TOTAL_DURATION:
            log_status(agent_id, "✅ Shift Complete. Exiting.")
            break

        driver = None
        browser_start_time = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Engine...")
            driver = get_driver(agent_id)
            
            driver.get("https://www.instagram.com/")
            WebDriverWait(driver, 30).until(lambda d: "instagram" in d.current_url)
            
            clean_session = extract_session_id(cookie)
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/'})
            
            driver.refresh()
            time.sleep(5) 
            
            if "login" in driver.current_url:
                log_status(agent_id, "❌ Login Failed.")
                driver.quit()
                break

            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(8) 
            log_status(agent_id, "✅ Connected.")

            while (time.time() - browser_start_time) < BROWSER_LIFESPAN:
                if (time.time() - global_start_time) > TOTAL_DURATION: break
                
                msg_box = find_mobile_box(driver)
                if msg_box:
                    msg = random.choice(messages)
                    # Use the new GHOST FIX function
                    if adaptive_inject(driver, msg_box, f"{msg}"):
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        log_status(agent_id, f"✅ Sent message ({GLOBAL_SENT})")
                
                time.sleep(BASE_SPEED)

        except Exception as e:
            log_status(agent_id, "🔄 Connection glitch. Rebooting...")
        
        finally:
            if driver: 
                try: driver.quit()
                except: pass
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

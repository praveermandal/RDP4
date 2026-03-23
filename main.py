import os
import time
import re
import random
import datetime
import threading
import sys
import gc
import tempfile
from concurrent.futures import ThreadPoolExecutor

# 📦 SELENIUM & DRIVER TOOLS
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 🔥 ULTRA-SPEED V100 CONFIGURATION ---
THREADS = 3             
TOTAL_DURATION = 25000  
BURST_MIN = 0.04        # Slightly increased to 40ms to ensure stability
BURST_MAX = 0.06        
SESSION_MAX_SEC = 180   

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
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        
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
        return driver

def find_mobile_box(driver):
    """Aggressive search for the Instagram DM input box."""
    selectors = [
        "//textarea[@placeholder='Message...']",
        "//div[@role='textbox']",
        "//textarea",
        "//div[@contenteditable='true']",
        "//div[contains(@class, 'xat24cr')]" # New common IG class
    ]
    for xpath in selectors:
        try: 
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_status((By.XPATH, xpath)))
            if element.is_displayed():
                return element
        except: continue
    return None

def adaptive_inject(driver, element, text):
    try:
        # Use JS to force focus and insert text instantly
        driver.execute_script("arguments[0].focus();", element)
        driver.execute_script("document.execCommand('insertText', false, arguments[0]);", text)
        time.sleep(0.01)
        element.send_keys(Keys.ENTER)
        return True
    except Exception as e:
        return False

def get_dynamic_block(target_name):
    emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"]
    selected_emoji = random.choice(emojis)
    underlines = "________________________" 
    line = f"【 {target_name} 】 SAY P R V R बाप {selected_emoji} {underlines}/"
    block = "\n".join([line for _ in range(20)])
    return f"{block}\n⚡ ID: {random.randint(100000, 999999)}"

def run_life_cycle(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        try:
            log_status(agent_id, "🚀 Launching Heavy Agent...")
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Go directly to the chat
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(7) # Increased load time for GitHub's network speed

            msg_box = find_mobile_box(driver)
            
            if not msg_box:
                log_status(agent_id, "❌ Could not find text box. Retrying session...")
                driver.quit()
                continue

            while (time.time() - session_start) < SESSION_MAX_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break
                
                final_text = get_dynamic_block(target_name)
                
                if adaptive_inject(driver, msg_box, final_text):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                        if GLOBAL_SENT % 10 == 0:
                            print(f"📈 Total Sent: {GLOBAL_SENT}", flush=True)
                
                time.sleep(random.uniform(BURST_MIN, BURST_MAX))
                
        except Exception as e:
            log_status(agent_id, f"⚠️ Error: {e}")
        finally:
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

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

# 📦 STANDARD SELENIUM + STEALTH
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- V100 CONFIGURATION (DUAL TURBO) ---
THREADS = 2             
TOTAL_DURATION = 25000  # ⚠️ 7 Hours (Guarantees Overlap for God Mode)

# ⚡ HYPER SPEED
BURST_SPEED = (0.1, 0.3) 

# ♻️ RESTART CYCLES (RAM SAVER)
SESSION_MIN_SEC = 300   # 5 Mins
SESSION_MAX_SEC = 600   # 10 Mins

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    # 🔒 Launch Lock: Prevents CPU spike by launching agents one by one
    with BROWSER_LAUNCH_LOCK:
        time.sleep(2) 
        chrome_options = Options()
        
        # 📉 ULTRA LITE WINDOWS FLAGS
        chrome_options.page_load_strategy = 'eager' # V100 Speed Boost
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--renderer-process-limit=2")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # MOBILE EMULATION (iPhone X Mode)
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Random Temp Folder (Prevents cache conflicts)
        custom_temp_dir = os.path.join(tempfile.gettempdir(), f"st_v100_{agent_id}_{random.randint(100,999)}")
        chrome_options.add_argument(f"--user-data-dir={custom_temp_dir}")

        driver = webdriver.Chrome(options=chrome_options)

        # 🪄 APPLY STEALTH
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'platform', {get: () => 'Linux armv8l'});
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});
            """
        })

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
        driver.custom_temp_path = custom_temp_dir
        return driver

def find_mobile_box(driver):
    # Fast Selector (No waiting)
    selectors = ["//textarea", "//div[@role='textbox']"]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            return el
        except: continue
    return None

def adaptive_inject(driver, element, text):
    try:
        # ⚡ JS INJECTION (INSTANT TYPE)
        # We click first to ensure focus
        driver.execute_script("arguments[0].click();", element)
        
        # Random Noise to bypass Spam Filter
        noise = random.randint(1000, 9999)
        final_text = f"{text} "

        driver.execute_script("""
            var el = arguments[0];
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, final_text)
        
        # Zero Sleep for max speed
        
        try:
            # ⚡ JS CLICK (INSTANT SEND)
            btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
            driver.execute_script("arguments[0].click();", btn)
        except:
            element.send_keys(Keys.ENTER)
        return True
    except:
        return False

def inject_full_cookies(driver, raw_cookie_string):
    try:
        cookie_parts = raw_cookie_string.split(';')
        for part in cookie_parts:
            if '=' in part:
                name, value = part.strip().split('=', 1)
                try:
                    driver.add_cookie({
                        'name': name.strip(), 
                        'value': value.strip(), 
                        'path': '/', 
                        'domain': '.instagram.com'
                    })
                except: pass
        return True
    except: return False

def run_life_cycle(agent_id, cookie, target, messages):
    # 🕒 STAGGER: Agent 2 waits 45s to let Agent 1 stabilize RAM
    if agent_id == 2:
        log_status(agent_id, "[WAIT] Holding 45s for Agent 1...")
        time.sleep(45)

    global_start = time.time()

    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        temp_path = None
        current_session_limit = random.randint(SESSION_MIN_SEC, SESSION_MAX_SEC)
        session_start = time.time()
        
        try:
            log_status(agent_id, "[START] Launching Browser...")
            driver = get_driver(agent_id)
            temp_path = getattr(driver, 'custom_temp_path', None)
            
            driver.get("https://www.instagram.com/")
            inject_full_cookies(driver, cookie)
            driver.refresh()
            # Wait for login validation
            time.sleep(random.uniform(4, 6)) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)
            
            # Popup Killer
            try: driver.execute_script("document.querySelector('button._a9--').click()")
            except: pass
            
            # 📢 AGENT 1 OPENING SHOUT
            if agent_id == 1:
                log_status(agent_id, "📢 Sending Activation Ping...")
                try:
                    box = find_mobile_box(driver)
                    if box: adaptive_inject(driver, box, "Bot Active! 🚀 ")
                except: pass

            log_status(agent_id, "[SUCCESS] Connected. Starting Turbo Loop.")
            msg_box = find_mobile_box(driver)

            while (time.time() - session_start) < current_session_limit:
                if (time.time() - global_start) > TOTAL_DURATION: break

                if not msg_box:
                    msg_box = find_mobile_box(driver)
                    if not msg_box:
                        time.sleep(1)
                        continue

                msg = random.choice(messages)
                if adaptive_inject(driver, msg_box, f"{msg} "):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                    log_status(agent_id, "[SENT] Message delivered")
                
                # ⚡ HYPER SPEED DELAY
                wait_time = random.uniform(*BURST_SPEED)
                time.sleep(wait_time)

        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            log_status(agent_id, f"[ERROR] Glitch: {err_msg[:50]}...")
        
        finally:
            log_status(agent_id, "[CLEAN] Recycling RAM...")
            if driver: 
                try: driver.quit()
                except: pass
            
            if temp_path and os.path.exists(temp_path):
                try: shutil.rmtree(temp_path, ignore_errors=True)
                except: pass
            
            gc.collect() 
            time.sleep(3) 

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")
    
    if len(cookie) < 5:
        sys.exit(1)

    # Clean old processes
    try: subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()

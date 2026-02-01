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

# --- V95 PASSIVE CONFIGURATION ---
THREADS = 2             # ✅ Dual Agent
TOTAL_DURATION = 25000  # ⚠️ 7 HOURS (Guarantees Overlap with Schedule)

# ⚡ SPEED SETTINGS
BURST_SPEED = (0.2, 0.5) 
SESSION_MIN_SEC = 180   
SESSION_MAX_SEC = 300   

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    with BROWSER_LAUNCH_LOCK:
        time.sleep(2) 
        chrome_options = Options()
        
        # ⚡ PERFORMANCE & STEALTH
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--renderer-process-limit=1")
        chrome_options.add_argument("--js-flags=--max_old_space_size=128")
        chrome_options.add_argument("--disk-cache-size=1") 
        chrome_options.add_argument("--media-cache-size=1") 
        
        # 🚫 BLOCK ASSETS (Saves RAM)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.cookies": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 📱 MOBILE SPOOFING
        mobile_emulation = {
            "deviceMetrics": { "width": 360, "height": 800, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 📁 ISOLATED TEMP FOLDER
        custom_temp_dir = os.path.join(tempfile.gettempdir(), f"passive_v95_{agent_id}_{int(time.time())}")
        chrome_options.add_argument(f"--user-data-dir={custom_temp_dir}")

        driver = webdriver.Chrome(options=chrome_options)

        # 🧬 CDP INJECTION (Verification Bypass)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'platform', {get: () => 'Linux armv8l'});
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});
            """
        })

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux armv8l",
            webgl_vendor="ARM",
            renderer="Mali-G76",
            fix_hairline=True,
        )
        
        driver.custom_temp_path = custom_temp_dir
        return driver

def find_mobile_box(driver):
    try: return driver.find_element(By.XPATH, "//textarea")
    except: pass
    try: return driver.find_element(By.XPATH, "//div[@role='textbox']")
    except: pass
    return None

def adaptive_inject(driver, element, text):
    try:
        # 🛡️ GHOSTBUSTER NOISE (Anti-Spam)
        noise = random.randint(1000, 9999)
        final_text = f"{text} " 
        
        # ⚡ JS INJECTION
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, final_text)
        
        time.sleep(0.05) 
        
        # ⚡ BLIND CLICK
        try:
            driver.execute_script("document.querySelector('div[role=button]').click();")
        except:
            element.send_keys(Keys.ENTER)
        return True
    except: return False

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
    # Stagger start to save CPU
    if agent_id == 2:
        time.sleep(60)

    global_start = time.time()

    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        temp_path = None
        current_session_limit = random.randint(SESSION_MIN_SEC, SESSION_MAX_SEC)
        session_start = time.time()
        
        try:
            log_status(agent_id, "[START] Launching...")
            driver = get_driver(agent_id)
            temp_path = getattr(driver, 'custom_temp_path', None)
            
            driver.get("https://www.instagram.com/")
            inject_full_cookies(driver, cookie)
            driver.refresh()
            time.sleep(random.uniform(3, 5)) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(4)
            
            # Popup Killer
            try: driver.execute_script("document.querySelector('button._a9--').click()")
            except: pass
            
            log_status(agent_id, "[SUCCESS] Connected.")
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
                
                wait_time = random.uniform(*BURST_SPEED)
                time.sleep(wait_time)

        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            log_status(agent_id, f"[ERROR] Glitch: {err_msg[:50]}...")
        
        finally:
            log_status(agent_id, "[CLEAN] Resetting Session...")
            if driver: 
                try: driver.quit()
                except: pass
            
            # 🧹 DELETE TEMP FILES
            if temp_path and os.path.exists(temp_path):
                try: shutil.rmtree(temp_path, ignore_errors=True)
                except: pass
            
            gc.collect() 
            time.sleep(5) 

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")
    
    if len(cookie) < 5:
        print("[FATAL] Cookie Missing")
        sys.exit(1)
    
    # 🧹 STARTUP CLEAN: Kill any old stuck Chrome processes
    try: subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()

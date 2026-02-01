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

# --- V95 REBORN CONFIGURATION ---
THREADS = 2             # ✅ 2 AGENTS (Dual Core)
TOTAL_DURATION = 21600  

# ⚡ SPEED (Safe for 2 Agents)
# We use a slightly safer speed to ensure both agents don't jam the CPU.
BURST_SPEED = (0.2, 0.5) 

# ♻️ INDIVIDUAL RESPAWN CYCLES
# Each agent will self-destruct and respawn independently every 3-5 mins.
SESSION_MIN_SEC = 180   
SESSION_MAX_SEC = 300   

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    # 🔒 Launch Lock: Agents take turns starting up to save CPU
    with BROWSER_LAUNCH_LOCK:
        time.sleep(2) 
        chrome_options = Options()
        
        # ⚡ ATOM CORE (V110 Tech)
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--headless=new") 
        
        # 📉 STRIPPED FLAGS
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--renderer-process-limit=1")
        chrome_options.add_argument("--js-flags=--max_old_space_size=128")
        chrome_options.add_argument("--disk-cache-size=1") 
        chrome_options.add_argument("--media-cache-size=1") 
        
        # 🚫 BLOCK ASSETS
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 📱 MOBILE EMULATION
        mobile_emulation = {
            "deviceMetrics": { "width": 360, "height": 800, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 📁 ISOLATED TEMP PROFILE (Vital for 2 Agents)
        # We create a unique folder so Agent 1 doesn't delete Agent 2's data
        custom_temp_dir = os.path.join(tempfile.gettempdir(), f"atom_v95_{agent_id}_{int(time.time())}")
        chrome_options.add_argument(f"--user-data-dir={custom_temp_dir}")

        driver = webdriver.Chrome(options=chrome_options)

        # 🧬 CDP INJECTION
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
        
        # Tag the driver with its folder so we can delete it later
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
        # 🛡️ GHOSTBUSTER INJECTION (V110 Tech)
        noise = random.randint(1000, 9999)
        final_text = f"{text} " # Simple space is usually enough for bulk

        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, final_text)
        
        time.sleep(0.05) 
        
        try:
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
    # 🕒 STAGGER: Agent 2 waits 60s so they don't respawn at the same time
    if agent_id == 2:
        log_status(agent_id, "[WAIT] Staggering start by 60s...")
        time.sleep(60)

    global_start = time.time()

    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        temp_path = None
        current_session_limit = random.randint(SESSION_MIN_SEC, SESSION_MAX_SEC)
        session_start = time.time()
        
        try:
            log_status(agent_id, "[START] Launching Atom Browser...")
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
            log_status(agent_id, "[CLEAN] Self-Destructing Session...")
            if driver: 
                try: driver.quit()
                except: pass
            
            # 🧹 SURGICAL CLEANUP
            # Only deletes THIS agent's temp folder
            if temp_path and os.path.exists(temp_path):
                try: shutil.rmtree(temp_path, ignore_errors=True)
                except: pass
            
            gc.collect() 
            time.sleep(5) # Brief cool-down before respawn

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")
    
    if len(cookie) < 5:
        print("[FATAL] Cookie error.")
        sys.exit(1)
    
    # Initial kill of any old processes
    try:
        subprocess.run("taskkill /F /IM chrome.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()

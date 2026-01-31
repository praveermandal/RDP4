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

# --- V78 SINGLE AGENT CONFIGURATION ---
THREADS = 1             # 👤 Single Agent (Maximum Safety)
BASE_SPEED = 0.5        
TOTAL_DURATION = 21300  # 5 Hours 55 Minutes

# ⏱️ STABILITY SETTING
# Browser restarts every 40 minutes to keep RAM usage low.
BROWSER_LIFESPAN = 2400 
RESTART_DELAY = 10      

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
    
    # 🍃 ECO-MODE
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disk-cache-size=1")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    
    # 🖥️ DESKTOP MODE
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_agent_{agent_id}_{random.randint(1000,9999)}")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def kill_popups(driver):
    try:
        popups = [
            "//button[text()='Not Now']",
            "//button[contains(text(), 'Not Now')]",
            "//div[@role='dialog']//button[text()='Not Now']"
        ]
        for xpath in popups:
            btns = driver.find_elements(By.XPATH, xpath)
            for btn in btns:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
    except:
        pass

def find_chat_box(driver):
    selectors = [
        "//div[@role='textbox']", 
        "//div[@contenteditable='true']", 
        "//div[contains(@aria-label, 'Message')]"
    ]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            if el.is_displayed(): return el
        except: continue
    return None

def react_safe_send(driver, element, text):
    try:
        element.click()
        driver.execute_script("arguments[0].value = '';", element)
        for char in text:
            element.send_keys(char)
        time.sleep(0.1) 
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
        element.send_keys(Keys.ENTER)
        return True
    except:
        return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    global_start_time = time.time()
    
    while True:
        if (time.time() - global_start_time) > TOTAL_DURATION:
            log_status(agent_id, "✅ Shift Complete. Exiting for restart.")
            break

        driver = None
        browser_start_time = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Desktop Engine...")
            driver = get_driver(agent_id)
            
            driver.get("https://www.instagram.com/")
            WebDriverWait(driver, 30).until(lambda d: "instagram" in d.current_url)
            
            clean_session = extract_session_id(cookie)
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/'})
            driver.refresh()
            time.sleep(5)
            
            kill_popups(driver)
            
            if "login" in driver.current_url:
                log_status(agent_id, "❌ Login Failed.")
                driver.quit()
                break

            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)
            kill_popups(driver)

            log_status(agent_id, "👀 Waiting for chat box...")
            try:
                WebDriverWait(driver, 30).until(lambda d: find_chat_box(d) is not None)
                log_status(agent_id, "⚡ Box Found! Starting Spam.")
            except:
                log_status(agent_id, "⚠️ Timeout. Retrying...")
                driver.quit()
                continue

            while (time.time() - browser_start_time) < BROWSER_LIFESPAN:
                if (time.time() - global_start_time) > TOTAL_DURATION: break
                
                msg_box = find_chat_box(driver)
                if msg_box:
                    msg = random.choice(messages)
                    if react_safe_send(driver, msg_box, f"{msg}"):
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        log_status(agent_id, "✅ Sent message")
                
                time.sleep(BASE_SPEED)

        except Exception as e:
            log_status(agent_id, "🔄 Connection drop. Rebooting...")
        
        finally:
            if driver: 
                try: driver.quit()
                except: pass
            gc.collect()
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

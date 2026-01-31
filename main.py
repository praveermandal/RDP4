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
from selenium.webdriver.support import expected_conditions as EC

# --- V68 CONFIGURATION ---
THREADS = 1             
BASE_SPEED = 0.8        
TOTAL_DURATION = 21000  
BROWSER_LIFESPAN = 1800 

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
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def brute_force_cookie(driver, session_id):
    """
    Tries to inject the cookie using 3 different domain strategies.
    """
    # Strategy 1: Automatic (Let browser decide)
    cookie_variants = [
        {'name': 'sessionid', 'value': session_id, 'path': '/'},
        {'name': 'sessionid', 'value': session_id, 'path': '/', 'domain': '.instagram.com'},
        {'name': 'sessionid', 'value': session_id, 'path': '/', 'domain': 'www.instagram.com'}
    ]
    
    driver.delete_all_cookies() # Clear slate
    
    for i, cookie in enumerate(cookie_variants):
        try:
            driver.add_cookie(cookie)
            log_status(1, f"🍪 Cookie Strategy {i+1} Success!")
            return True
        except Exception as e:
            # log_status(1, f"Strategy {i+1} Failed: {e}") # Debug only
            continue
            
    return False

def force_send_click(driver):
    xpaths = [
        "//div[text()='Send']",
        "//button[text()='Send']",
        "//div[@role='button' and text()='Send']"
    ]
    for xpath in xpaths:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                return True
        except:
            continue
    return False

def adaptive_inject(driver, element, text):
    try:
        element.click()
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, text)
        time.sleep(0.5)
        
        if force_send_click(driver):
            return True
        else:
            element.send_keys(Keys.ENTER)
            return True
    except:
        return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    global_start_time = time.time()
    
    while (time.time() - global_start_time) < TOTAL_DURATION:
        driver = None
        browser_start_time = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Browser...")
            driver = get_driver(agent_id)
            
            # 1. ROBUST CONNECTION
            driver.get("https://www.instagram.com/")
            
            # Wait until we are strictly on the domain
            WebDriverWait(driver, 20).until(lambda d: "instagram.com" in d.current_url)
            time.sleep(2) 

            # 2. BRUTE FORCE INJECTION
            clean_session = extract_session_id(cookie)
            if not brute_force_cookie(driver, clean_session):
                log_status(agent_id, "❌ CRITICAL: All cookie strategies failed.")
                log_status(agent_id, f"Current URL: {driver.current_url}")
                driver.quit()
                return

            driver.refresh()
            time.sleep(5) 
            
            # 3. VERIFY LOGIN
            if "login" in driver.current_url:
                log_status(agent_id, "❌ Login Failed. Session ID is invalid/expired.")
                driver.quit()
                return

            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(8)
            log_status(agent_id, "✅ Connected.")

            while (time.time() - browser_start_time) < BROWSER_LIFESPAN:
                if (time.time() - global_start_time) > TOTAL_DURATION: break

                try:
                    msg_box = driver.find_element(By.XPATH, "//textarea | //div[@role='textbox'] | //div[@contenteditable='true']")
                    msg = random.choice(messages)
                    if adaptive_inject(driver, msg_box, f"{msg} "):
                        log_status(agent_id, f"Sent: {msg}")
                    else:
                        log_status(agent_id, "⚠️ Failed to send.")

                except:
                    time.sleep(5)
                
                time.sleep(BASE_SPEED)

        except Exception as e:
            log_status(agent_id, f"❌ Error: {e}")
            time.sleep(10)
        
        finally:
            if driver: 
                try: driver.quit()
                except: pass
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

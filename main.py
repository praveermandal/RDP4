import os
import time
import random
import shutil
import undetected_chromedriver as uc
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- V63 CONFIGURATION ---
THREADS = 1             
# ⚡ OPTIMIZED RESOLUTION (720p)
SCREEN_RES = (1280, 720)  
BASE_SPEED = (0.2, 0.5) 

def log_status(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] 🖥️ V63 RDP (720p): {msg}", flush=True)

def get_rdp_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 📉 LOW RES OPTIMIZATION
    # Force the browser to match the virtual screen exactly
    options.add_argument(f"--window-size={SCREEN_RES[0]},{SCREEN_RES[1]}")
    
    # Block heavy assets to save RAM
    prefs = {"profile.managed_default_content_settings.images": 2} # Block Images
    options.add_experimental_option("prefs", prefs)

    # 🎭 PERSISTENT PROFILE (Keeps you logged in)
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")

    # Start the Driver
    driver = uc.Chrome(options=options, version_main=None) 
    return driver

def human_type(element, text):
    """Simulates physical key presses."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*BASE_SPEED))
    time.sleep(0.5)
    element.send_keys(Keys.ENTER)

def main():
    # 1. START LIGHTWEIGHT VIRTUAL MONITOR (720p)
    log_status(f"🖥️ Booting Virtual Display ({SCREEN_RES[0]}x{SCREEN_RES[1]})...")
    display = Display(visible=0, size=SCREEN_RES)
    display.start()
    
    driver = None
    try:
        log_status("🚀 Launching Chrome in GUI Mode...")
        driver = get_rdp_driver()
        
        # 2. Login Check
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        # If we see the login page, inject cookie
        if "login" in driver.current_url:
            log_status("🍪 Injecting Session Cookie...")
            cookie = os.environ.get("INSTA_COOKIE", "").strip()
            if "sessionid=" in cookie:
                cookie = cookie.split("sessionid=")[1].split(";")[0].strip()
            
            driver.add_cookie({'name': 'sessionid', 'value': cookie, 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(5)
        else:
            log_status("✅ Session restored from profile!")

        # 3. Target Navigation
        target = os.environ.get("TARGET_THREAD_ID", "").strip()
        messages = os.environ.get("MESSAGES", "Hello").split("|")
        
        driver.get(f"https://www.instagram.com/direct/t/{target}/")
        time.sleep(8)
        
        # 4. The Loop
        log_status("⚡ Starting Simulation Loop...")
        start_time = time.time()
        
        while (time.time() - start_time) < 1200: # 20 mins
            try:
                # Find the box
                box = driver.find_element(By.XPATH, "//div[@contenteditable='true'] | //textarea")
                box.click()
                
                msg = random.choice(messages)
                human_type(box, msg)
                
                log_status(f"✅ Sent: {msg}")
                
                # Wait 2-5 seconds
                time.sleep(random.uniform(2.0, 5.0))
                
            except Exception as e:
                log_status(f"⚠️ Glitch: {e}")
                driver.refresh()
                time.sleep(10)

    except Exception as e:
        log_status(f"❌ Crash: {e}")
    finally:
        if driver: driver.quit()
        display.stop()

if __name__ == "__main__":
    main()

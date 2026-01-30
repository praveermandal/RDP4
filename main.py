import os
import time
import random
import subprocess
import shutil
import undetected_chromedriver as uc
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- V63.1 CONFIGURATION ---
THREADS = 1             
SCREEN_RES = (1280, 720)  
BASE_SPEED = (0.2, 0.5) 

def log_status(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] 🖥️ V63.1 RDP: {msg}", flush=True)

def get_chrome_version():
    """
    🔍 Detects the installed Chrome version on the Runner.
    """
    try:
        # Ask Linux for the version string
        result = subprocess.check_output(["google-chrome", "--version"]).decode("utf-8")
        # Extract the main version number (e.g., "144")
        version = result.strip().split()[-1].split(".")[0]
        log_status(f"Detected Chrome Version: {version}")
        return int(version)
    except Exception as e:
        log_status(f"⚠️ Could not detect Chrome version: {e}")
        return None

def get_rdp_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={SCREEN_RES[0]},{SCREEN_RES[1]}")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")

    # 🔒 VERSION LOCK FIX
    # We explicitly tell uc to use the version we found
    detected_version = get_chrome_version()
    
    # If detection failed, default to 144 (Current Stable)
    target_version = detected_version if detected_version else 144

    # Start the Driver with version_main specified
    driver = uc.Chrome(options=options, version_main=target_version) 
    return driver

def human_type(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*BASE_SPEED))
    time.sleep(0.5)
    element.send_keys(Keys.ENTER)

def main():
    log_status(f"🖥️ Booting Virtual Display ({SCREEN_RES[0]}x{SCREEN_RES[1]})...")
    display = Display(visible=0, size=SCREEN_RES)
    display.start()
    
    driver = None
    try:
        log_status("🚀 Launching Chrome in GUI Mode...")
        driver = get_rdp_driver()
        
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        
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

        target = os.environ.get("TARGET_THREAD_ID", "").strip()
        messages = os.environ.get("MESSAGES", "Hello").split("|")
        
        driver.get(f"https://www.instagram.com/direct/t/{target}/")
        time.sleep(8)
        
        log_status("⚡ Starting Simulation Loop...")
        start_time = time.time()
        
        while (time.time() - start_time) < 1200: 
            try:
                box = driver.find_element(By.XPATH, "//div[@contenteditable='true'] | //textarea")
                box.click()
                
                msg = random.choice(messages)
                human_type(box, msg)
                
                log_status(f"✅ Sent: {msg}")
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

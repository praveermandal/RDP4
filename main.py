# -*- coding: utf-8 -*-
import os, time, random, datetime, tempfile, threading
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ STRIKE CONFIG ---
TABS_PER_MACHINE = 5  
BURST_DELAY = 0.05    # Fast but allows the UI to register the "Send"
TOTAL_DURATION = 25000 

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v100_hybrid_{agent_id}_{int(time.time())}")
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

def find_box(driver):
    selectors = ["//div[@role='textbox']", "//textarea", "//*[@contenteditable='true']"]
    for xpath in selectors:
        try: return driver.find_element(By.XPATH, xpath)
        except: continue
    return None

def agent_worker(driver, handle, target_name):
    """Each tab gets its own thread to hammer the 'Send' button independently."""
    driver.switch_to.window(handle)
    time.sleep(10) # Heavy wait for chat load
    
    msg_box = find_box(driver)
    if not msg_box:
        print("❌ Could not find message box in this tab.")
        return

    emojis = ["👑", "⚡", "🔥", "💎", "⚔️", "🔱", "🧿", "🌪️"]
    
    while True:
        try:
            # 1. Generate the 20-line block
            emoji = random.choice(emojis)
            line = f"【 {target_name} 】 SAY P R V R बाप {emoji} ____________________/"
            block = "\n".join([line for _ in range(20)])
            final_text = f"{block}\n⚡ ID: {random.randint(1000, 9999)}"

            # 2. The 'Original' Method (Guaranteed to trigger Send button)
            driver.execute_script("arguments[0].focus();", msg_box)
            driver.execute_script("document.execCommand('insertText', false, arguments[0]);", final_text)
            msg_box.send_keys(Keys.ENTER)
            
            # 3. Burst Delay
            time.sleep(BURST_DELAY)
            
        except Exception as e:
            print(f"⚠️ Tab Error: {e}")
            break

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA")
    
    driver = get_driver("hybrid_runner")
    
    try:
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        print(f"🚀 Spawning {TABS_PER_MACHINE} Working Nodes...")
        for i in range(TABS_PER_MACHINE):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            time.sleep(5)

        handles = driver.window_handles[1:]
        
        threads = []
        for handle in handles:
            t = threading.Thread(target=agent_worker, args=(driver, handle, target_name))
            t.daemon = True
            t.start()
            threads.append(t)

        # Keep main process alive
        time.sleep(TOTAL_DURATION)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

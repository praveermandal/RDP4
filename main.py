# -*- coding: utf-8 -*-
import os, time, re, random, datetime, threading, sys, gc, tempfile, shutil
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ V101.6 HYPER-SPEED CONFIG ---
TABS_PER_MACHINE = 3    
PURGE_INTERVAL = 120    # ♻️ Nuclear restart every 2 mins
STRIKE_SPEED = 180      # 180ms - Pure JS Speed

sys.stdout.reconfigure(encoding='utf-8')

def log_status(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [Phoenix V101.6]: {msg}", flush=True)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # 🛑 CRITICAL FOR SPEED: Keep background tabs alive
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-background-timer-throttling")
    
    chrome_options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v101_nuke_{int(time.time())}")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def deploy_hyper_engine(driver, target_id, target_name):
    """Spawns 3 Tabs and injects an independent JS loop into each."""
    
    for i in range(TABS_PER_MACHINE):
        tab_idx = i + 1
        log_status(f"🌐 Loading Tab {tab_idx}...")
        driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
        # ⏳ Reduced stagger to 6s for faster start
        time.sleep(6) 

    handles = driver.window_handles[1:]
    
    for idx, handle in enumerate(handles):
        try:
            driver.switch_to.window(handle)
            # Fast Injection: No Python waiting inside this loop
            driver.execute_script(f"""
                const targetName = "{target_name}";
                const pulse = {STRIKE_SPEED};
                const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                
                const baseLines = 20;
                const adjustment = targetName.length - 4;
                const underscores = "_".repeat(Math.max(5, baseLines - adjustment));

                window.strikeInterval = setInterval(() => {{
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"], textarea');
                    if (box) {{
                        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                        const salt = Math.random().toString(36).substring(7).toUpperCase();
                        const line = `【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} ${{underscores}}/`;
                        const block = Array(22).fill(line).join('\\n') + "\\n⚡ ID: " + salt;

                        box.focus();
                        document.execCommand('insertText', false, block);
                        box.dispatchEvent(new Event('input', {{ bubbles: true }}));

                        const enter = new KeyboardEvent('keydown', {{
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        }});
                        box.dispatchEvent(enter);

                        // Wipe UI memory every 50ms to keep it fast
                        setTimeout(() => {{ if(box) box.innerHTML = ""; }}, 50);
                    }}
                }}, pulse);
            """)
            log_status(f"✅ Tab {idx+1}: Engine Firing.")
        except: pass

    log_status(f"🔥 ALL STREAMS SYNCED. Total Start Time: ~35s.")

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    
    if not cookie or not target_id: return

    while True:
        driver = None
        try:
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            # Login
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            deploy_hyper_engine(driver, target_id, target_name)
            
            # 🛑 CRITICAL: Python sleeps here while the BROWSER does the work
            time.sleep(PURGE_INTERVAL)
            
        except Exception as e:
            log_status(f"⚠️ Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()
            time.sleep(2)

if __name__ == "__main__":
    main()

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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🚀 ENGINE CONFIGURATION ---
THREADS = 3             
TOTAL_DURATION = 25000  
JS_DELAY = 30 # 30ms pulse

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
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
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v100_js_{agent_id}_{int(time.time())}")
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

def run_js_engine(agent_id, cookie, target_id, target_name):
    driver = None
    try:
        log_status(agent_id, "🚀 Initializing JS-Engine...")
        driver = get_driver(agent_id)
        driver.get("https://www.instagram.com/")
        
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
        driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
        time.sleep(10) # Heavy wait to ensure chat loads

        # Doubled {{ }} to escape Python f-string formatting
        js_payload = f"""
        const targetName = "{target_name}";
        const delay = {JS_DELAY};
        const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"];

        async function startPhoenix() {{
            while (true) {{
                try {{
                    const msgBox = document.querySelector('textarea, [role="textbox"], [contenteditable="true"]');
                    if (!msgBox) continue;

                    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const lines = Array(20).fill(`【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} ________________________/`).join('\\n');
                    const finalMsg = lines + "\\n⚡ ID: " + Math.floor(Math.random() * 999999);

                    msgBox.focus();
                    document.execCommand('insertText', false, finalMsg);
                    
                    const enterEvent = new KeyboardEvent('keydown', {{
                        bubbles: true, cancelable: true, keyCode: 13, key: 'Enter'
                    }});
                    msgBox.dispatchEvent(enterEvent);
                    
                    await new Promise(r => setTimeout(r, delay));
                }} catch (e) {{ console.log("JS Error: ", e); }}
            }}
        }}
        startPhoenix();
        """

        log_status(agent_id, "🔥 JS Payload Injected. Monitoring...")
        driver.execute_script(js_payload)

        # Keep browser open to allow JS to run
        end_time = time.time() + TOTAL_DURATION
        while time.time() < end_time:
            time.sleep(10)

    except Exception as e:
        log_status(agent_id, f"⚠️ Python Error: {e}")
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
            executor.submit(run_js_engine, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

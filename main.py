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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🚀 ENGINE CONFIGURATION ---
THREADS = 3             
TOTAL_DURATION = 25000  
JS_DELAY = 40 

sys.stdout.reconfigure(encoding='utf-8')
DRIVER_PATH = None

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    global DRIVER_PATH
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

    service = Service(DRIVER_PATH)
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
        
        sid = cookie.replace("sessionid=", "").strip().split(";")[0]
        
        try:
            driver.add_cookie({'name': 'sessionid', 'value': sid, 'domain': '.instagram.com'})
            log_status(agent_id, "✅ Cookie Injected")
        except Exception as ce:
            log_status(agent_id, f"⚠️ Cookie Error: {ce}")

        driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
        log_status(agent_id, "⏳ Waiting for chat to load...")
        time.sleep(15)

        # Doubled {{ }} to escape Python's f-string parser
        js_payload = f"""
        (async function() {{
            const targetName = "{target_name}";
            const delay = {JS_DELAY};
            const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"];

            function getMessageBox() {{
                return document.querySelector('textarea') || 
                       document.querySelector('[role="textbox"]') || 
                       document.querySelector('[contenteditable="true"]') ||
                       document.querySelector('.xat24cr');
            }}

            while (true) {{
                try {{
                    const msgBox = getMessageBox();
                    if (!msgBox) {{
                        await new Promise(r => setTimeout(r, 1000));
                        continue;
                    }}

                    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const lines = Array(20).fill(`【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} ________________________/`).join('\\n');
                    const finalMsg = lines + "\\n⚡ ID: " + Math.floor(Math.random() * 999999);

                    msgBox.focus();
                    msgBox.click();
                    
                    document.execCommand('insertText', false, finalMsg);
                    
                    const enterEvent = new KeyboardEvent('keydown', {{
                        bubbles: true, cancelable: true, keyCode: 13, key: 'Enter', which: 13
                    }});
                    msgBox.dispatchEvent(enterEvent);
                    
                    await new Promise(r => setTimeout(r, delay));
                }} catch (e) {{ 
                    console.error("JS Error", e); 
                }}
            }}
        }})();
        """

        log_status(agent_id, "🔥 JS Engine Firing...")
        driver.execute_script(js_payload)

        # Keep browser open
        end_time = time.time() + TOTAL_DURATION
        while time.time() < end_time:
            time.sleep(20)

    except Exception as e:
        log_status(agent_id, f"❌ Engine Crash: {e}")
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

    global DRIVER_PATH
    print("📦 Installing Chrome Driver...", flush=True)
    DRIVER_PATH = ChromeDriverManager().install()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_js_engine, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

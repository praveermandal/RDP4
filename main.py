import os
import time
import random
import datetime
import threading
import sys
import gc
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor

# 📦 SELENIUM & DRIVER TOOLS
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🔥 SPEED & ENDURANCE CONFIGURATION ---
THREADS = 2             
TOTAL_DURATION = 250000 

# ⚡ TIMING SETTINGS
JS_DELAY = 50           # 50ms (Ultra-Speed)
REFRESH_CYCLE = 120     # Soft Refresh every 2 minutes
HARD_RESET_CYCLE = 1800 # Kill and restart Chrome every 30 mins

sys.stdout.reconfigure(encoding='utf-8')
DRIVER_PATH = None
INSTALL_LOCK = threading.Lock()

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def cleanup_temp_dirs(agent_id):
    temp_dir_base = tempfile.gettempdir()
    for item in os.listdir(temp_dir_base):
        if item.startswith(f"automa_{agent_id}_"):
            try:
                shutil.rmtree(os.path.join(temp_dir_base, item), ignore_errors=True)
            except:
                pass

def get_driver(agent_id):
    global DRIVER_PATH
    with INSTALL_LOCK:
        if DRIVER_PATH is None:
            log_status(agent_id, "📦 Installing Chrome Driver...")
            DRIVER_PATH = ChromeDriverManager().install()

    cleanup_temp_dirs(agent_id) 
    
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
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"automa_{agent_id}_{int(time.time())}")
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

def run_prvr_engine(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        hard_reset_timer = time.time()
        
        try:
            log_status(agent_id, "🚀 Launching Fresh Browser Profile...")
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = cookie.replace("sessionid=", "").strip().split(";")[0]
            driver.add_cookie({'name': 'sessionid', 'value': sid, 'domain': '.instagram.com'})
            
            while (time.time() - hard_reset_timer) < HARD_RESET_CYCLE:
                try:
                    driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
                    time.sleep(12) 

                    # --- ⚡ HYPER-OPTIMIZED 50ms PAYLOAD ---
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

                                // 🛑 CRITICAL FIX: Manually wipe the box before IG has a chance to
                                if (msgBox.innerHTML !== '') {{
                                    msgBox.innerHTML = '';
                                }}

                                const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                                const traceID = Math.random().toString(36).substring(2, 9).toUpperCase();
                                
                                const line = `【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} __________/`;
                                const block = Array(22).fill(line).join('\\n');
                                const finalMsg = block + "\\n⚡ ID: " + traceID;

                                msgBox.focus();
                                document.execCommand('insertText', false, finalMsg);
                                msgBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                
                                // Give React 15ms to render the Send button
                                await new Promise(r => setTimeout(r, 15)); 
                                
                                const sendBtn = document.querySelector('div.xjyslct') || 
                                                Array.from(document.querySelectorAll('div[role="button"]')).find(el => el.textContent.trim().toLowerCase() === 'send');
                                
                                if (sendBtn) {{ 
                                    sendBtn.click(); 
                                }} else {{
                                    const enterEvent = new KeyboardEvent('keydown', {{ bubbles: true, cancelable: true, keyCode: 13, key: 'Enter' }});
                                    msgBox.dispatchEvent(enterEvent);
                                }}

                                await new Promise(r => setTimeout(r, delay));
                            }} catch (e) {{ 
                                console.error("JS Loop Error", e); 
                            }}
                        }}
                    }})();
                    """

                    log_status(agent_id, f"🔥 Firing 22-Line Blocks at {JS_DELAY}ms...")
                    driver.execute_script(js_payload)

                    time.sleep(REFRESH_CYCLE)
                    log_status(agent_id, "♻️ 2-Min Soft Refresh...")
                    driver.refresh()
                    
                except Exception as loop_err:
                    log_status(agent_id, f"⚠️ Cycle Error: {loop_err}. Retrying in 10s...")
                    time.sleep(10)

            log_status(agent_id, "🛑 30-Minute Hard Reset Reached. Nuking Browser...")

        except Exception as e:
            log_status(agent_id, f"❌ Session Crash: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()
            time.sleep(5) 

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "PRVR") 
    
    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_prvr_engine, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

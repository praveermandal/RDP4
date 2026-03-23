# -*- coding: utf-8 -*-
# 🚀 PHOENIX V100.85 (CLICK-PATCH EDITION)
# 🛡️ 2 AGENTS | 5 TABS EACH | 10 THREADS TOTAL
# ⚡ SPEED: 180ms NATIVE JS PULSE | 2-MIN HARD RESTART CYCLE

import os
import time
import re
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

# --- 🔥 CONFIGURATION ---
THREADS = 2              
TABS_PER_MACHINE = 5     
TOTAL_DURATION = 25000   
SESSION_MAX_SEC = 120    
PULSE_DELAY = 180        

sys.stdout.reconfigure(encoding='utf-8')
BROWSER_LAUNCH_LOCK = threading.Lock()
DRIVER_PATH = None

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def cleanup_temp_dirs(agent_id):
    temp_dir_base = tempfile.gettempdir()
    for item in os.listdir(temp_dir_base):
        if item.startswith(f"v100_{agent_id}_"):
            try:
                shutil.rmtree(os.path.join(temp_dir_base, item), ignore_errors=True)
            except: pass

def get_driver(agent_id):
    global DRIVER_PATH
    with BROWSER_LAUNCH_LOCK:
        if DRIVER_PATH is None:
            DRIVER_PATH = ChromeDriverManager().install()
        
        time.sleep(2) 
        cleanup_temp_dirs(agent_id)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        
        # 📱 Mobile Emulation is active - Requires physical clicks
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"v100_{agent_id}_{int(time.time())}")
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

def inject_hyper_engine(driver, handle, tab_index, target_name):
    try:
        driver.switch_to.window(handle)
        
        js_payload = f"""
            const targetName = "{target_name}";
            const pulse = {PULSE_DELAY};
            const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️", "🐍", "🦍"];
            
            const baseUnderlines = 24;
            const adjustment = targetName.length - 4;
            const numUnderlines = Math.max(5, baseUnderlines - adjustment);
            const underlines = "_".repeat(numUnderlines);

            if (window.hyperEngine) clearInterval(window.hyperEngine);

            window.hyperEngine = setInterval(() => {{
                // 🛑 Restored Automa selectors
                const box = document.querySelector('.xat24cr') || 
                            document.querySelector('textarea') || 
                            document.querySelector('div[role="textbox"]') || 
                            document.querySelector('[contenteditable="true"]');
                
                if (box) {{
                    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const salt = Math.floor(Math.random() * 8999 + 1000); 
                    
                    const line = `【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} ${{underlines}}/`;
                    const block = Array(20).fill(line).join('\\n');
                    const finalText = block + "\\n⚡ ID: " + salt;

                    // 🛑 CRITICAL: The Missing Click
                    box.click();
                    box.focus();
                    
                    document.execCommand('insertText', false, finalText);
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));

                    // Small delay to let React process the input before hitting send
                    setTimeout(() => {{
                        const sendBtn = document.querySelector('.xjyslct') || 
                                        Array.from(document.querySelectorAll('div[role="button"]')).find(el => el.textContent && el.textContent.trim().toLowerCase() === 'send');
                        
                        if (sendBtn) {{
                            sendBtn.click();
                        }} else {{
                            const enter = new KeyboardEvent('keydown', {{
                                bubbles: true, cancelable: true, key: 'Enter', keyCode: 13
                            }});
                            box.dispatchEvent(enter);
                        }}
                        
                        // Clear Box
                        setTimeout(() => {{ if(box) box.innerHTML = ""; }}, 40);
                    }}, 20);
                }}
            }}, pulse);
        """
        driver.execute_script(js_payload)
        print(f"✅ Agent | Tab {tab_index}: Engine Synced @ {PULSE_DELAY}ms.")
    except Exception as e:
        print(f"⚠️ Agent | Tab {tab_index}: Injection Failed -> {e}")

def run_life_cycle(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        try:
            log_status(agent_id, "🚀 Launching Mobile Browser...")
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            log_status(agent_id, f"🌐 Spawning {TABS_PER_MACHINE} Direct Chats...")
            for i in range(TABS_PER_MACHINE):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(8) 

            handles = driver.window_handles[1:] 
            
            for idx, handle in enumerate(handles):
                inject_hyper_engine(driver, handle, idx + 1, target_name)
            
            log_status(agent_id, "🔥 ALL TABS FIRING! Entering 2-minute cruise phase...")

            while (time.time() - session_start) < SESSION_MAX_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break
                time.sleep(10) 
                
        except Exception as e:
            log_status(agent_id, f"⚠️ Session Error: {e}")
        finally:
            log_status(agent_id, "♻️ 2-Minute Mark Reached: Full Restart & RAM Flush")
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA")
    
    if not cookie or not target_id:
        print("❌ Missing Secrets (INSTA_COOKIE or TARGET_THREAD_ID)!")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

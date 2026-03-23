# -*- coding: utf-8 -*-
# 🚀 PHOENIX V100.90 (DOM-FORCE EDITION)
# ⚡ TARGET: 180ms PULSE | 5 TABS SYNC
# 🛡️ FIX: FORCED REACT STATE HYDRATION

import os, time, re, random, datetime, threading, sys, gc, tempfile, shutil
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
THREADS = 2              
TABS_PER_MACHINE = 5     
SESSION_MAX_SEC = 120    
PULSE_DELAY = 180        

sys.stdout.reconfigure(encoding='utf-8')
BROWSER_LAUNCH_LOCK = threading.Lock()
DRIVER_PATH = None

def get_driver(agent_id):
    global DRIVER_PATH
    with BROWSER_LAUNCH_LOCK:
        if DRIVER_PATH is None: DRIVER_PATH = ChromeDriverManager().install()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
        temp_dir = os.path.join(tempfile.gettempdir(), f"v100_{agent_id}_{int(time.time())}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=chrome_options)
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL", fix_hairline=True)
        return driver

def inject_hyper_engine(driver, handle, tab_index, target_name):
    try:
        driver.switch_to.window(handle)
        js_payload = f"""
            const targetName = "{target_name}";
            const pulse = {PULSE_DELAY};
            const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱"];
            
            if (window.hyperEngine) clearInterval(window.hyperEngine);

            window.hyperEngine = setInterval(() => {{
                // Try multiple selectors
                const box = document.querySelector('div[aria-label="Message..."]') || 
                            document.querySelector('.xat24cr') || 
                            document.querySelector('div[contenteditable="true"]');
                
                if (box) {{
                    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const salt = Math.random().toString(36).substring(7).toUpperCase();
                    const line = `【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} __________/`;
                    const finalText = Array(20).fill(line).join('\\n') + "\\n⚡ ID: " + salt;

                    // 1. Force Focus & Click
                    box.focus();
                    const clickEv = new MouseEvent('click', {{view: window, bubbles: true, cancelable: true}});
                    box.dispatchEvent(clickEv);
                    
                    // 2. Clear and Insert
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, finalText);

                    // 3. Force React to see the change
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    box.dispatchEvent(new Event('change', {{ bubbles: true }}));

                    // 4. Find and Click Send Button
                    setTimeout(() => {{
                        const sendBtn = document.querySelector('.xjyslct') || 
                                        Array.from(document.querySelectorAll('div[role="button"]')).find(el => el.innerText === 'Send');
                        
                        if (sendBtn) {{
                            sendBtn.click();
                        }} else {{
                            // Fallback to Enter Key
                            const enter = new KeyboardEvent('keydown', {{bubbles: true, cancelable: true, key: 'Enter', keyCode: 13}});
                            box.dispatchEvent(enter);
                        }}
                    }}, 30);
                }}
            }}, pulse);
        """
        driver.execute_script(js_payload)
        print(f"✅ Tab {tab_index}: Active")
    except Exception as e: print(f"⚠️ Tab {tab_index} Err: {e}")

def run_life_cycle(agent_id, cookie, target_id, target_name):
    while True:
        driver = None
        session_start = time.time()
        try:
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            for i in range(TABS_PER_MACHINE):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(10) # Heavy stagger for stability

            handles = driver.window_handles[1:] 
            for idx, handle in enumerate(handles):
                inject_hyper_engine(driver, handle, idx + 1, target_name)
            
            while (time.time() - session_start) < SESSION_MAX_SEC:
                time.sleep(10)
        except Exception: pass
        finally:
            if driver: driver.quit()
            gc.collect()

def main():
    c, t, n = os.environ.get("INSTA_COOKIE"), os.environ.get("TARGET_THREAD_ID"), os.environ.get("TARGET_NAME", "EZRA")
    if not c or not t: return
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        for i in range(THREADS): ex.submit(run_life_cycle, i+1, c, t, n)

if __name__ == "__main__": main()

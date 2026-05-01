# -*- coding: utf-8 -*-
import os, time, re, random, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ V100 TUNED SETTINGS ---
THREADS = 2             
TABS_PER_THREAD = 2      
PULSE_DELAY = 100       
SESSION_MAX_SEC = 120   
TOTAL_DURATION = 25000  

sys.stdout.reconfigure(encoding='utf-8')

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie_raw, target_id, target_name):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Initializing Browser...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            time.sleep(4) 
            
            # --- FULL COOKIE INJECTION ---
            print(f"🔑 [Agent {agent_id}] Injecting Session Tokens...")
            for item in cookie_raw.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    driver.add_cookie({'name': key, 'value': value, 'domain': '.instagram.com', 'path': '/'})
            
            for i in range(TABS_PER_THREAD):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                print(f"📂 [Agent {agent_id}] Opened Target Tab {i+1}")
                time.sleep(2)

            handles = driver.window_handles[1:]
            for idx, handle in enumerate(handles):
                driver.switch_to.window(handle)
                time.sleep(3) # Wait for DM UI to load
                
                # Check if we are actually logged in
                if "login" in driver.current_url:
                    print(f"❌ [Agent {agent_id} Tab {idx}] ERROR: Redirected to Login. Cookies expired!")
                    continue

                print(f"✅ [Agent {agent_id} Tab {idx}] Logic Injected. Starting Burst...")
                
                driver.execute_script("""
                    const name = arguments[0];
                    const delay = arguments[1];
                    let sentCount = 0;
                    
                    function getBlock(n) {
                        const emojis = ["⭕", "🌀", "🔴", "💠", "🧿", "🔘"];
                        const emo = emojis[Math.floor(Math.random() * emojis.length)];
                        const line = `(${n}) 𝚂ᴀ𝚈 【﻿ＰＲＶ𝐑】 𝐃ᴀ𝐃𝐃𝐘 ~${emo}\\n`;
                        let block = "";
                        for(let i=0; i<22; i++) { block += line; }
                        return block + "\\n⚡ ID: " + Math.random().toString(36).substring(7);
                    }

                    const tracker = setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const text = getBlock(name);
                            box.focus();
                            document.execCommand('insertText', false, text);
                            box.dispatchEvent(new Event('input', { bubbles: true }));

                            const enter = new KeyboardEvent('keydown', {
                                bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                            });
                            box.dispatchEvent(enter);
                            
                            sentCount++;
                            if(sentCount % 10 === 0) console.log("SENT_STATUS: " + sentCount + " messages sent.");
                            
                            setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                        } else {
                            console.log("SENT_STATUS: ERROR - Textbox not found");
                        }
                    }, delay);
                """, target_name, PULSE_DELAY)

            # Monitor JS Console for status
            cycle_start = time.time()
            while time.time() - cycle_start < SESSION_MAX_SEC:
                for handle in handles:
                    driver.switch_to.window(handle)
                    logs = driver.get_log('browser')
                    for entry in logs:
                        if "SENT_STATUS" in entry['message']:
                            print(f"📊 [Agent {agent_id}] {entry['message']}")
                time.sleep(10)

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Cycle Error: {e}")
            if driver:
                driver.save_screenshot(f"error_agent_{agent_id}.png")
                print(f"📸 [Agent {agent_id}] Screenshot saved to workspace.")
        finally:
            if driver: driver.quit()
            gc.collect() 
            time.sleep(2)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")

    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, cookie, target_id, target_name))
        t.start()
        threads.append(t)
        time.sleep(10)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

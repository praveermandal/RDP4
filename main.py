# -*- coding: utf-8 -*-
import os, time, random, sys, datetime, tempfile, shutil
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ CONFIGURATION ---
TABS_PER_MACHINE = 5  
PULSE_MS = 90  # Target speed: ~90ms (Adjustable)
TOTAL_DURATION = 25000 

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.page_load_strategy = 'eager'
    
    # --- ORIGINAL MOBILE EMULATION ---
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    # Unique temp profile for this runner
    temp_dir = os.path.join(tempfile.gettempdir(), f"v100_hyper_{agent_id}_{int(time.time())}")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # --- ORIGINAL STEALTH SETTINGS ---
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux armv8l", 
        webgl_vendor="ARM",
        renderer="Mali-G76",
        fix_hairline=True,
    )
    return driver

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "EZRA")
    
    if not cookie or not target_id:
        print("❌ Missing Secrets (INSTA_COOKIE or TARGET_THREAD_ID)!")
        return

    driver = get_driver("main_runner")
    
    try:
        # 1. Login
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🔑 Handshake...")
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        # 2. Spawn Hyper-Tabs
        print(f"🚀 Spawning {TABS_PER_MACHINE} Android Tabs...")
        for i in range(TABS_PER_MACHINE):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            time.sleep(6) # Necessary for hydration on mobile layout

        handles = driver.window_handles[1:]
        
        # 3. ⚡ THE JS ENGINE INJECTION
        for idx, handle in enumerate(handles):
            driver.switch_to.window(handle)
            driver.execute_script("""
                const targetName = arguments[0];
                const pulseRate = arguments[1];
                const emojis = ["👑", "⚡", "🔥", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                
                console.log("🔥 HYPER-INJECT ACTIVE");

                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"], textarea');
                    if (box) {
                        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                        const underlines = "_".repeat(Math.max(5, 24 - (targetName.length - 4)));
                        const line = `【 ${targetName} 】 SAY P R V R बाप ${emoji} ${underlines}/`;
                        const block = new Array(20).fill(line).join('\\n');
                        const finalText = `${block}\\n⚡ ID: ${Math.floor(Math.random() * 9999)}`;

                        // Native Lexical Injection
                        box.focus();
                        document.execCommand('insertText', false, finalText);
                        box.dispatchEvent(new Event('input', { bubbles: true }));

                        // Keyboard Event
                        const enter = new KeyboardEvent('keydown', {
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        });
                        box.dispatchEvent(enter);

                        // Anti-Lag: Clear DOM
                        setTimeout(() => { if(box.innerHTML) box.innerHTML = ""; }, 5);
                    }
                }, pulseRate);
            """, target_name, PULSE_MS)
            print(f"✅ Tab {idx+1} Inject Success.")

        # Keep session alive
        time.sleep(TOTAL_DURATION)

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

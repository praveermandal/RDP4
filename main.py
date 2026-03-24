import os, time, re, random, datetime, threading, sys, gc, tempfile, shutil
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🔥 LIGHTWEIGHT SPEED CONFIG ---
TABS_PER_AGENT = 1       # Reduced to 1 for 100% CPU stability
PURGE_INTERVAL = 180     
STRIKE_SPEED_MS = 150    # Faster pulse to compensate for 1 tab

sys.stdout.reconfigure(encoding='utf-8')

def log_status(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [Phoenix V103.9]: {msg}", flush=True)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--disable-background-networking")
    
    # Lighter Android Emulation
    mobile_emulation = {
        "deviceMetrics": { "width": 360, "height": 740, "pixelRatio": 2.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v103_light_{int(time.time())}")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Android", fix_hairline=True)
    return driver

def inject_striker(driver, handle, target_name):
    driver.switch_to.window(handle)
    driver.execute_script(f"""
        const targetName = "{target_name}";
        const speed = {STRIKE_SPEED_MS};
        const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱"];
        const underscores = "_".repeat(Math.max(5, 24 - (targetName.length - 4)));

        function startStriker() {{
            if (window.prvrStriker) clearInterval(window.prvrStriker);
            
            window.prvrStriker = setInterval(() => {{
                // Robust selector for mobile DM box
                const box = document.querySelector('div[role="textbox"], [contenteditable="true"], textarea');
                if (box) {{
                    const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const salt = Math.random().toString(36).substring(7).toUpperCase();
                    
                    // DOUBLE BLOCK: Sends 40 lines total in one go to maximize 1 tab
                    const line = `【 ${{targetName}} 】 SAY P R V R बाप ${{emoji}} ${{underscores}}/`;
                    const block = Array(40).fill(line).join('\\n') + "\\n⚡ ID: " + salt;

                    box.focus();
                    document.execCommand('insertText', false, block);
                    box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    
                    const enter = new KeyboardEvent('keydown', {{
                        bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                    }});
                    box.dispatchEvent(enter);
                    
                    setTimeout(() => {{ if(box) box.innerHTML = ""; }}, 5);
                }}
            }}, speed);
        }}

        const checkExist = setInterval(() => {{
           const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
           if (box) {{
              clearInterval(checkExist);
              startStriker();
           }}
        }}, 1000); 
    """)

def run_life_cycle(cookie, target_id, target_name):
    while True:
        driver = None
        try:
            log_status("🛠️ Initializing Lightweight Engine V103.9...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Direct navigation to Chat (Skips unnecessary page loads)
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(15) # Essential: Let the CPU breathe

            # Check if login redirected us back
            if "login" in driver.current_url:
                log_status("❌ FATAL: Cookie Expired.")
                sys.exit(1)

            log_status("💉 Syncing High-Capacity Stream...")
            inject_striker(driver, driver.current_window_handle, target_name)
            
            time.sleep(PURGE_INTERVAL)
                
        except Exception as e:
            log_status(f"⚠️ Error: {e}")
            time.sleep(5)
        finally:
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    run_life_cycle(cookie, target_id, target_name)

if __name__ == "__main__":
    main()

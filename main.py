import os, time, re, random, datetime, threading, sys, gc, tempfile, shutil
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🚀 V106.1 RAM-FLUSH SPEED PORT ---
THREADS = 2 
BURST_MIN = 0.04  # Pushed to 40ms
BURST_MAX = 0.07 
SESSION_MAX_SEC = 120    

sys.stdout.reconfigure(encoding='utf-8')
LAUNCH_LOCK = threading.Lock()

def get_driver(agent_id):
    with LAUNCH_LOCK:
        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--blink-settings=imagesEnabled=false")
        
        mobile = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        options.add_experimental_option("mobileEmulation", mobile)
        
        temp = os.path.join(tempfile.gettempdir(), f"v106_1_{agent_id}_{int(time.time())}")
        options.add_argument(f"--user-data-dir={temp}")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

def run_life_cycle(agent_id, cookie, target_id, target_name):
    while True:
        driver = None
        session_start = time.time()
        try:
            print(f"[{agent_id}] 🚀 Launching Engine...", flush=True)
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(6) # Essential for initial load

            while (time.time() - session_start) < SESSION_MAX_SEC:
                # 🔄 Generate Block
                emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱"]
                line = f"【 {target_name} 】 SAY P R V R बाप {random.choice(emojis)} ________________________/"
                block = "\n".join([line for _ in range(20)]) + f"\n⚡ ID: {random.randint(1000, 9999)}"
                
                try:
                    # ⚡ FIND BOX
                    box = driver.find_element(By.XPATH, "//div[@role='textbox']|//textarea")
                    
                    # ⚡ INSTANT INJECT
                    driver.execute_script("""
                        var el = arguments[0];
                        var txt = arguments[1];
                        el.focus();
                        document.execCommand('insertText', false, txt);
                        
                        // 🔥 THE RAM FLUSH: Clear internal state after dispatch
                        setTimeout(() => { if(el) el.innerHTML = ""; }, 5);
                    """, box, block)
                    
                    # ⚡ SEND
                    box.send_keys(Keys.ENTER)
                    
                except:
                    break 
                
                # ⚡ Minimal sleep to prevent CPU thread lock
                time.sleep(random.uniform(BURST_MIN, BURST_MAX))
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target_id, target_name)

if __name__ == "__main__":
    main()

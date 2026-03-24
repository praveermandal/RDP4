import os, time, re, random, datetime, threading, sys, gc, tempfile
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🚀 V110 DOUBLE-BUFFERED ENGINE ---
THREADS = 2 
BURST_MIN = 0.01  # 🔥 10ms (The absolute floor for Python)
BURST_MAX = 0.03 
SESSION_MAX_SEC = 120    

def get_driver(agent_id):
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
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def run_life_cycle(agent_id, cookie, target_id, target_name):
    while True:
        driver = None
        session_start = time.time()
        try:
            driver = get_driver(agent_id)
            driver.get("https://www.instagram.com/")
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(6)

            # 🎯 CACHE THE BOX
            box = driver.find_element(By.XPATH, "//div[@role='textbox']|//textarea")

            while (time.time() - session_start) < SESSION_MAX_SEC:
                # 🔄 Generate 2 Unique Blocks in Python to bypass JS randomness overhead
                emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱"]
                
                def make_block():
                    line = f"【 {target_name} 】 SAY P R V R बाप {random.choice(emojis)} ________________________/"
                    return "\\n".join([line for _ in range(20)]) + f"\\n⚡ ID: {random.randint(1000, 9999)}"

                block1 = make_block()
                block2 = make_block()

                try:
                    # ⚡ DOUBLE-TAP INJECTION
                    # We send TWO blocks and TWO Enters in ONE single Selenium command.
                    driver.execute_script("""
                        var el = arguments[0];
                        var b1 = arguments[1];
                        var b2 = arguments[2];
                        
                        function fire(txt) {
                            el.focus();
                            document.execCommand('insertText', false, txt);
                            el.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, key:'Enter', code:'Enter', keyCode:13}));
                        }

                        fire(b1);
                        setTimeout(() => { fire(b2); }, 5); // 5ms gap between the double-tap
                        
                        // RAM Wipe
                        setTimeout(() => { if(el) el.innerHTML = ""; }, 15);
                    """, box, block1, block2)
                    
                except:
                    break 
                
                # ⚡ Nearly zero sleep
                time.sleep(random.uniform(BURST_MIN, BURST_MAX))
                
        except: pass
        finally:
            if driver: driver.quit()
            gc.collect()

def main():
    cookie = os.environ.get("INSTA_COOKIE", "")
    target_id = os.environ.get("TARGET_THREAD_ID", "")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS): executor.submit(run_life_cycle, i+1, cookie, target_id, target_name)

if __name__ == "__main__": main()

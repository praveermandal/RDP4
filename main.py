import os, time, re, random, datetime, threading, sys, gc, tempfile
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 🚀 V111 TRIPLE-BUFFERED ENGINE ---
THREADS = 2 
BURST_MIN = 0.005  # 🔥 5ms (Hardware Limit)
BURST_MAX = 0.015  # 🔥 15ms
SESSION_MAX_SEC = 120    

def get_driver(agent_id):
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-v8-idle-tasks") # 🔥 Disables JS pauses
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
                # 🔄 Generate 3 Unique Blocks in Python 
                emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱"]
                
                def make_block():
                    line = f"【 {target_name} 】 SAY P R V R बाप {random.choice(emojis)} ________________________/"
                    return "\\n".join([line for _ in range(20)]) + f"\\n⚡ ID: {random.randint(1000, 9999)}"

                b1, b2, b3 = make_block(), make_block(), make_block()

                try:
                    # ⚡ TRIPLE-TAP INJECTION (The "Slingshot")
                    driver.execute_script("""
                        var el = arguments[0];
                        var msgs = [arguments[1], arguments[2], arguments[3]];
                        
                        msgs.forEach((txt, index) => {
                            setTimeout(() => {
                                el.focus();
                                document.execCommand('insertText', false, txt);
                                // Native Event Dispatcher (Faster than send_keys)
                                el.dispatchEvent(new KeyboardEvent('keydown', {
                                    bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                                }));
                                // Small clear to keep the box responsive
                                if (index === msgs.length - 1) {
                                    setTimeout(() => { el.innerHTML = ""; }, 10);
                                }
                            }, index * 2); // 2ms gap between each block inside the browser
                        });
                    """, box, b1, b2, b3)
                    
                except:
                    break 
                
                # ⚡ Absolute minimum thread sleep
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

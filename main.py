import os
import time
import random
import datetime
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
THREADS = 2           # 2 Browsers running in parallel
BURST_SIZE = 8        # Send 8 messages per burst
CYCLE_DELAY = 1.0     # Wait 1s between bursts
LIFE_DURATION = 300   # Restart browser every 5 Minutes (300s)
LOG_FILE = "message_log.txt"

# GLOBAL COUNTER (Tracks total across all restarts)
GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()

def log_speed(agent_id, current_life_sent, start_time):
    """Logs speed + Global Total"""
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    speed = current_life_sent / elapsed
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Read Global Total safely
    with COUNTER_LOCK:
        total = GLOBAL_SENT
        
    entry = f"[{timestamp}] ⚡ Agent {agent_id} | Session Total: {total} | Speed: {speed:.1f} msg/s"
    print(entry, flush=True)
    try:
        with open(LOG_FILE, "a") as f: f.write(entry + "\n")
    except: pass

def get_driver(agent_id):
    """Creates a fresh, clean browser instance"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    
    # 🚨 CRITICAL FIX: Prevents the "0x55cab..." Crash
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Random temp folder ensures no cache conflicts or file lock errors
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_p_{agent_id}_{random.randint(1,99999)}")
    
    # Rotate User Agent
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12{agent_id+5}.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def instant_inject(driver, element, text):
    driver.execute_script("""
        var elm = arguments[0], txt = arguments[1];
        elm.focus();
        document.execCommand('insertText', false, txt);
        elm.dispatchEvent(new Event('input', {bubbles: true}));
    """, element, text)

def run_life_cycle(agent_id, session_id, target_input, messages):
    driver = None
    sent_in_this_life = 0
    start_time = time.time()
    
    try:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ♻️ Agent {agent_id}: Rebirthing Browser...", flush=True)
        driver = get_driver(agent_id)
        
        driver.get("https://www.instagram.com/")
        clean_session = session_id.split("sessionid=")[1].split(";")[0] if "sessionid=" in session_id else session_id
        driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'domain': '.instagram.com', 'path': '/'})
        driver.refresh()
        time.sleep(5)

        driver.get(f"https://www.instagram.com/direct/t/{target_input}/")
        time.sleep(5)
        
        box_xpath = "//div[@contenteditable='true']"
        msg_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, box_xpath)))

        # 5-MINUTE TIMER LOOP
        while (time.time() - start_time) < LIFE_DURATION:
            try:
                for _ in range(BURST_SIZE):
                    msg = random.choice(messages)
                    jitter = "⠀" * random.randint(0, 1)
                    instant_inject(driver, msg_box, f"{msg}{jitter}")
                    msg_box.send_keys(Keys.ENTER)
                    
                    # Update Counts
                    sent_in_this_life += 1
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                        
                    # --- RANDOMIZED DELAY (150ms to 200ms) ---
                    # Prevents "Perfect Machine" detection
                    time.sleep(random.uniform(0.15, 0.20))
                
                log_speed(agent_id, sent_in_this_life, start_time)
                time.sleep(CYCLE_DELAY)

            except Exception:
                break # Restart immediately on error
        
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⏰ Agent {agent_id}: 5 Minutes Up. Refreshing...", flush=True)
                
    except Exception as e:
        print(f"⚠️ Agent {agent_id} Error: {e}", flush=True)
    finally:
        if driver:
            try: driver.quit()
            except: pass
        # Force Clean Temp Folder (Prevents Disk Full Crash)
        try: shutil.rmtree(f"/tmp/chrome_p_{agent_id}", ignore_errors=True)
        except: pass

def agent_worker(agent_id, session_id, target_input, messages):
    while True:
        run_life_cycle(agent_id, session_id, target_input, messages)
        time.sleep(2)

def main():
    print(f"🔥 V18.4 PHOENIX STABLE | 5-MIN REFRESH | {THREADS} THREADS", flush=True)
    
    session_id = os.environ.get("INSTA_SESSION", "").strip()
    target_input = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not session_id: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, session_id, target_input, messages)

if __name__ == "__main__":
    main()

import os, time, re, random, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- 🔥 PERFORMANCE CONFIG ---
THREADS = 2             # Parallel browser instances
TABS_PER_THREAD = 3     # Multi-tab injection (Total 6 Agents)
PULSE_DELAY = 100       # 100ms precise firing
SESSION_MAX_SEC = 300   # Restart browser every 5 mins to clear cache/RAM

sys.stdout.reconfigure(encoding='utf-8')

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager' # Don't wait for full page load
    
    # iPad Pro emulation for optimized DOM layout
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def deploy_hyper_inject(driver, target_id, target_name):
    """Deploys the JS Firing Engine into the browser tabs."""
    try:
        # Launch specialized tabs
        for _ in range(TABS_PER_THREAD):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            time.sleep(2)

        handles = driver.window_handles[1:]
        for handle in handles:
            driver.switch_to.window(handle)
            # ⚡ THE JS HYPER-ENGINE ⚡
            driver.execute_script("""
                const target = arguments[0];
                const delay = arguments[1];
                
                function generateBlock(name) {
                    const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                    const emo = emojis[Math.floor(Math.random() * emojis.length)];
                    const line = `【 ${name} 】 SAY P R V R बाप ${emo} ____________________/\\n`;
                    let block = "";
                    for(let i=0; i<20; i++) { block += line; }
                    return block + "\\n⚡ ID: " + Math.random().toString(36).substring(7);
                }

                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const text = generateBlock(target);
                        box.focus();
                        document.execCommand('insertText', false, text);
                        box.dispatchEvent(new Event('input', { bubbles: true }));

                        const enter = new KeyboardEvent('keydown', {
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        });
                        box.dispatchEvent(enter);
                        
                        // Instant clear to prevent DOM lag
                        setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                    }
                }, delay);
            """, target_name, PULSE_DELAY)
        return True
    except: return False

def agent_worker(agent_id, cookie, target_id, target_name):
    while True:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Initializing Hyper-Engine...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            # Cleanly extract sessionid
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            if deploy_hyper_inject(driver, target_id, target_name):
                print(f"🔥 [Agent {agent_id}] ALL TABS FIRING AT {PULSE_DELAY}ms")
                time.sleep(SESSION_MAX_SEC) # Run for 5 mins
            
        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()
            time.sleep(5)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie or not target_id:
        print("❌ ERROR: Missing Secrets (INSTA_COOKIE / TARGET_THREAD_ID)")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=agent_worker, args=(i+1, cookie, target_id, target_name))
        t.start()
        threads.append(t)
        time.sleep(10) # Stagger browser launches to prevent CPU spike

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

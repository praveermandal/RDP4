# -*- coding: utf-8 -*-
import os, time, re, random, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚡ V100 HYPER-ENGINE SETTINGS (PULSE TUNED) ---
THREADS = 2             
TABS_PER_THREAD = 2     
PULSE_DELAY = 85        # Precision tuned for 80-100ms actual speed
SESSION_MAX_SEC = 60    # Fast resets prevent memory leaks and lag
TOTAL_DURATION = 25000  

sys.stdout.reconfigure(encoding='utf-8')

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.page_load_strategy = 'eager'
    # High-performance mobile emulation for iPad Pro
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Stealth parameters to bypass basic automation detection
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie, target_id):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Pulse Shift Starting...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            # Clean sessionid from cookie string
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Ignite multiple tabs
            for _ in range(TABS_PER_THREAD):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(2)

            handles = driver.window_handles[1:]
            for handle in handles:
                driver.switch_to.window(handle)
                
                # ⚡ BURST-FIRE JS ENGINE
                driver.execute_script("""
                    const delay = arguments[0];
                    
                    function getBlock() {
                        const emojis = ["⭕", "🌀", "🔴", "💠", "🧿", "🔘"];
                        const emo = emojis[Math.floor(Math.random() * emojis.length)];
                        
                        // FONT-STYLED MESSAGES (PRVR KO BAAP BANA LE)
                        const styles = [
                            `❮❮ ⚡ 𝐏𝐑𝐕𝐑 𝐊𝐎 𝐁𝐀𝐀𝐏 𝐁𝐀𝐍𝐀 𝐋𝐄 ⚡ ❯❯`,
                            `▓▒░  𝗣𝗥𝗩𝗥 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗔𝗡𝗔 𝗟𝗘  ░▒▓`,
                            `╔══ 👑 𝐏𝐑𝐕𝐑 𝐊𝐎 𝐁𝐀𝐀𝐏 𝐁𝐀𝐍𝐀 𝐋𝐄 👑 ══╗`,
                            `◢◤ 🪬 𝗣𝗥𝗩𝗥 𝗞𝗢 𝗕𝗔𝗔𝗣 𝗕𝗔𝐍𝐀 𝐋𝐄 🪬 ◥◣`
                        ];
                        const selectedStyle = styles[Math.floor(Math.random() * styles.length)];
                        const line = `${selectedStyle} ~${emo}\\n`;
                        
                        let block = "";
                        for(let i=0; i<7; i++) { block += line; }
                        return block + "\\n⚡ ID: " + Math.random().toString(36).substring(7);
                    }

                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const text = getBlock();
                            box.focus();
                            document.execCommand('insertText', false, text);
                            box.dispatchEvent(new Event('input', { bubbles: true }));

                            const enter = new KeyboardEvent('keydown', {
                                bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                            });
                            box.dispatchEvent(enter);
                            
                            // Visual clearing for anti-lag
                            setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                        }
                    }, delay);
                """, PULSE_DELAY)

            print(f"🔥 [Agent {agent_id}] Waterfall Ignited (Reset in 60s)")
            time.sleep(SESSION_MAX_SEC) 

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Cycle Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect() 
            time.sleep(2)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")

    if not cookie or not target_id:
        print("❌ Missing Secrets! Check INSTA_COOKIE and TARGET_THREAD_ID.")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, cookie, target_id))
        t.start()
        threads.append(t)
        time.sleep(10) # Staggered startup to avoid CPU spike

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()

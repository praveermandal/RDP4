# -*- coding: utf-8 -*-
import os, time, random, datetime, tempfile
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ THE SWEET SPOT CONFIG ---
TABS_PER_MACHINE = 5  
PULSE_MS = 150  # Lowering slightly to 150ms to ensure the "Send" button actually clicks.
TOTAL_DURATION = 25000 

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.page_manager_check_interval = "0"
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v100_final_{agent_id}_{int(time.time())}")
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

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
        print("❌ Missing Secrets!")
        return

    driver = get_driver("final_runner")
    
    try:
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        print(f"🚀 Initializing {TABS_PER_MACHINE} High-Speed Nodes...")
        for i in range(TABS_PER_MACHINE):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            time.sleep(7) # Increased wait to ensure the chat fully loads before injecting

        handles = driver.window_handles[1:]
        
        for idx, handle in enumerate(handles):
            driver.switch_to.window(handle)
            
            # --- THE CLIPBOARD PASTE ENGINE ---
            driver.execute_script("""
                const targetName = arguments[0];
                const pulseRate = arguments[1];
                const emojis = ["👑", "⚡", "🔥", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                
                console.log("🔥 ENGINE ONLINE");

                setInterval(() => {
                    try {
                        const box = document.querySelector('div[role="textbox"]');
                        if (!box) return;

                        // Create the 20-line block
                        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                        const line = `【 ${targetName} 】 SAY P R V R बाप ${emoji} ____________________/`;
                        const finalText = new Array(20).fill(line).join('\\n') + `\\nID: ${Math.random().toString(36).substr(2, 5)}`;

                        // Fast Focus
                        box.focus();
                        
                        // Use execCommand 'insertText' - it's the only one that forces React to see the change instantly
                        document.execCommand('insertText', false, finalText);

                        // Find and Click Send (Check for multiple possible button states)
                        const sendButton = [...document.querySelectorAll('div[role="button"]')].find(el => el.innerText === 'Send' || el.querySelector('polyline'));
                        
                        if (sendButton) {
                            sendButton.click();
                        } else {
                            // Manual Enter fallback
                            const ke = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13 });
                            box.dispatchEvent(ke);
                        }

                        // DOM Cleanup to prevent lag
                        if(box.innerText.length > 0) { box.innerHTML = ""; }

                    } catch (e) { console.log("Pulse skipped: " + e); }
                }, pulseRate);
            """, target_name, PULSE_MS)
            print(f"✅ Node {idx+1} is firing.")

        # Keep alive loop
        while True:
            time.sleep(100)
            # Check if driver is still alive
            _ = driver.current_url

    except Exception as e:
        print(f"⚠️ FATAL: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

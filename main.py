# -*- coding: utf-8 -*-
import os, time, random, datetime, tempfile
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚡ HYPER-SPEED CONFIG ---
TABS_PER_MACHINE = 5  
PULSE_MS = 50  # 50ms is 20 messages per second per tab. 
TOTAL_DURATION = 25000 

def get_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.page_load_strategy = 'eager'
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"v100_ultra_{agent_id}_{int(time.time())}")
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

    driver = get_driver("ultra_runner")
    
    try:
        driver.get("https://www.instagram.com/")
        driver.add_cookie({'name': 'sessionid', 'value': cookie.strip(), 'domain': '.instagram.com'})
        
        print(f"🚀 Launching {TABS_PER_MACHINE} Ultra-Tabs...")
        for i in range(TABS_PER_MACHINE):
            driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            time.sleep(5) 

        handles = driver.window_handles[1:]
        
        for idx, handle in enumerate(handles):
            driver.switch_to.window(handle)
            # --- THE REACT STATE ENGINE ---
            driver.execute_script("""
                const targetName = arguments[0];
                const pulseRate = arguments[1];
                const emojis = ["👑", "⚡", "🔥", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                
                setInterval(() => {
                    try {
                        const box = document.querySelector('div[role="textbox"]');
                        if (!box) return;

                        // 1. Generate Block
                        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
                        const line = `【 ${targetName} 】 SAY P R V R बाप ${emoji} ____________________/`;
                        const finalText = new Array(20).fill(line).join('\\n') + `\\nID: ${Math.random()}`;

                        // 2. ULTRA-FAST INJECTION (Bypasses UI lag)
                        box.focus();
                        document.execCommand('insertText', false, finalText);
                        
                        // 3. FORCE SEND (Find the Send button via SVG Icon to be precise)
                        const sendBtn = document.evaluate("//div[@role='button'][text()='Send']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue 
                                        || document.querySelector('polyline[points="22 2 15 22 11 13 2 9 22 2"]')?.closest('div[role="button"]');
                        
                        if (sendBtn) {
                            sendBtn.click();
                        } else {
                            // Fallback to Enter Key if button not found
                            box.dispatchEvent(new KeyboardEvent('keydown', {bubbles: true, key: 'Enter', code: 'Enter', keyCode: 13}));
                        }

                        // 4. FLASH CLEAR (Keeps RAM at 0)
                        box.innerHTML = "";
                    } catch (e) {}
                }, pulseRate);
            """, target_name, PULSE_MS)
            print(f"✅ Tab {idx+1} Overclocked.")

        time.sleep(TOTAL_DURATION)

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

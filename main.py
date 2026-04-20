import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 3000    
SESSION_MAX_SEC = 200    

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        
        while True:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                    viewport={'width': 390, 'height': 844}
                )
                
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                
                # 📢 BRIDGE BROWSER LOGS TO TERMINAL
                page.on("console", lambda msg: print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True))

                print(f"🔗 [{full_id}] Connecting...", flush=True)
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=60000)
                
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Injection Running...", flush=True)

                await page.evaluate("""
                    ([targetName, mDelay, nDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            return `🔱 (${n}) 🌸 P R V R 🔱\\n${rail}\\n${rail}\\n${rail}\\n🔱 (${n}) 🌸 P R V R 🔱`;
                        }

                        // 📨 SPAMMER
                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(targetName));
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                            }
                        }, mDelay);

                        // 🛡️ NC WATCHDOG + LOGGER
                        setInterval(() => {
                            const header = document.querySelector('header');
                            if (header && !header.innerText.toLowerCase().includes(targetName.toLowerCase())) {
                                console.log("⚠️ NC detected wrong! Attempting change...");
                                
                                // Try to find ANY clickable element in the header (the 'i' or the name)
                                const infoBtn = document.querySelector('header svg[aria-label*="Details"]')?.parentElement || 
                                                document.querySelector('header div[role="button"]') ||
                                                header.querySelector('span');

                                if (infoBtn) {
                                    console.log("✅ Found Info button, clicking...");
                                    infoBtn.click();
                                    
                                    setTimeout(() => {
                                        const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"]');
                                        if (input) {
                                            console.log("📝 Input found, injecting name...");
                                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                            setter.call(input, ""); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            setter.call(input, targetName); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            
                                            setTimeout(() => {
                                                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                                                const save = btns.find(b => /save|done/i.test(b.innerText)) || 
                                                             document.querySelector('._acan, ._acap');
                                                
                                                if (save) {
                                                    console.log("🚀 Save button found, clicking!");
                                                    save.click();
                                                } else {
                                                    console.log("❌ Could not find Save button!");
                                                }
                                            }, 800);
                                        } else {
                                            console.log("❌ NC Input field not found in modal!");
                                        }
                                    }, 2000);
                                } else {
                                    console.log("❌ Could not find Header/Info button!");
                                }
                            }
                        }, nDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Error: {e}", flush=True)
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    print(f"💎 SYSTEM BOOTING...", flush=True)
    await asyncio.gather(*[run_agent(i+1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)])

if __name__ == "__main__":
    asyncio.run(main())

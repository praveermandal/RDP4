import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 CLUSTER SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 3000    # Check every 3 seconds
SESSION_MAX_SEC = 200    # Flush RAM every 3.3 minutes

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
        # Optimized launch for server-side headless
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", 
            "--disable-dev-shm-usage", 
            "--disable-gpu"
        ])
        
        while True:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                    viewport={'width': 390, 'height': 844}
                )
                
                # Cookie Extraction & Injection
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                
                # 📢 LIVE BROWSER LOGS TO TERMINAL
                page.on("console", lambda msg: print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True))

                print(f"🔗 [{full_id}] Connecting to Thread...", flush=True)
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=60000)
                
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED! Update GitHub Secret.", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Injection Running...", flush=True)

                # ⚡ HYPER-SPEED JAVASCRIPT INJECTION
                await page.evaluate("""
                    ([targetName, mDelay, nDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            return `🔱 (${n}) 🌸 P R V R 🔱\\n${rail}\\n${rail}\\n${rail}\\n🔱 (${n}) 🌸 P R V R 🔱`;
                        }

                        // 📨 SPAMMER ENGINE
                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(targetName));
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                            }
                        }, mDelay);

                        // 🛡️ NC WATCHDOG (NUCLEAR COORDINATE ATTACK)
                        setInterval(() => {
                            const header = document.querySelector('header');
                            if (header && !header.innerText.toLowerCase().includes(targetName.toLowerCase())) {
                                console.log("⚠️ NC Triggered! Searching for Details button...");
                                
                                // Wildcard search for Info/Details/Settings
                                const infoBtn = document.querySelector('[aria-label*="Details"], [aria-label*="Information"], [href*="details"], header div[role="button"]');

                                if (infoBtn) {
                                    console.log("🎯 Button identified. Force-clicking coordinates...");
                                    
                                    const rect = infoBtn.getBoundingClientRect();
                                    const x = rect.left + rect.width / 2;
                                    const y = rect.top + rect.height / 2;
                                    
                                    const clickEvt = new MouseEvent('click', {
                                        view: window, bubbles: true, cancelable: true, clientX: x, clientY: y
                                    });
                                    infoBtn.dispatchEvent(clickEvt);
                                    infoBtn.click(); // Double-tap

                                    setTimeout(() => {
                                        const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"], .x1i10hfl[type="text"]');
                                        if (input) {
                                            console.log("📝 Settings opened. Injecting new name...");
                                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                            setter.call(input, ""); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            setter.call(input, targetName); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            input.dispatchEvent(new Event('change', { bubbles: true }));
                                            
                                            setTimeout(() => {
                                                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                                                const save = btns.find(b => /save|done|update/i.test(b.innerText)) || 
                                                             document.querySelector('._acan, ._acap, button[type="button"].x1n2onr6');
                                                
                                                if (save) {
                                                    console.log("🚀 SAVE command sent!");
                                                    save.click();
                                                } else {
                                                    console.log("❌ Save button not found in sidebar.");
                                                }
                                            }, 1000);
                                        } else {
                                            console.log("❌ Sidebar opened but name input missing.");
                                        }
                                    }, 2000);
                                } else {
                                    console.log("❌ Could not find 'i' button in header.");
                                }
                            }
                        }, nDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY])

                # Run for SESSION_MAX_SEC before restarting to clear cache/RAM
                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [{full_id}] Cycle end. Restarting...", flush=True)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Error/Timeout: {e}. Restarting context...", flush=True)
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")

    if not cookie or not target_id:
        print("❌ [CRITICAL] Missing GitHub Secrets!", flush=True)
        return

    print(f"💎 V100 NODE {os.environ.get('MACHINE_NUMBER', '1')} INITIALIZED", flush=True)
    
    # Run AGENTS_PER_MACHINE concurrently
    tasks = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 CLUSTER SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 3000    
SESSION_MAX_SEC = 200    

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
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
                
                # Cookie Injection
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                
                # 📢 MIRROR BROWSER LOGS TO TERMINAL
                page.on("console", lambda msg: print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True))

                print(f"🔗 [{full_id}] Connecting to Thread...", flush=True)
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=60000)
                
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED! Reset your INSTA_COOKIE secret.", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Clusters Engaged", flush=True)

                # ⚡ HYPER-SPEED INJECTION (MESSAGES + AGGRESSIVE NC)
                await page.evaluate("""
                    ([targetName, mDelay, nDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            return `🔱 (${n}) 🌸 P R V R 🔱\\n${rail}\\n${rail}\\n${rail}\\n🔱 (${n}) 🌸 P R V R 🔱`;
                        }

                        // 📨 MESSAGE SPAMMER
                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(targetName));
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                                setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                            }
                        }, mDelay);

                        // 🛡️ NC WATCHDOG (FIXED & HARDENED)
                        setInterval(() => {
                            const titleEl = document.querySelector('header span[role="link"], .x1lliihq.x193iq5w, header h1, header span');
                            const currentName = titleEl ? titleEl.innerText : "";

                            if (currentName && !currentName.toLowerCase().includes(targetName.toLowerCase())) {
                                console.log("⚠️ NC MISMATCH! Clicking header to force settings...");
                                
                                // Triple-Click Strategy to wake up React
                                titleEl.click();
                                setTimeout(() => titleEl.click(), 200);

                                setTimeout(() => {
                                    const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"], .x1i10hfl[type="text"]');
                                    if (input) {
                                        console.log("📝 Settings Open. Forcing NC state...");
                                        
                                        // Focus and Hardware-level Clear
                                        input.focus();
                                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        
                                        setter.call(input, ""); 
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        
                                        setter.call(input, targetName); 
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        input.dispatchEvent(new Event('change', { bubbles: true }));
                                        
                                        setTimeout(() => {
                                            // Search for ALL possible Save/Done buttons
                                            const btns = Array.from(document.querySelectorAll('button, div[role="button"], span[role="button"]'));
                                            const save = btns.find(b => {
                                                const txt = b.innerText.toLowerCase();
                                                return txt.includes("save") || txt.includes("done") || txt.includes("update");
                                            }) || document.querySelector('._acan, ._acap, .x1n2onr6');
                                            
                                            if (save) {
                                                console.log("🚀 SAVE COMMAND SENT!");
                                                save.click();
                                                // Close sidebar if it lingers
                                                setTimeout(() => { if(document.body.contains(save)) save.click(); }, 300);
                                            } else {
                                                console.log("❌ NC Error: Save button hidden. Are you Admin?");
                                            }
                                        }, 1000);
                                    }
                                }, 2500);
                            }
                        }, nDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [{full_id}] Restarting Context...", flush=True)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Error: {e}. Reconnecting...", flush=True)
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")

    if not cookie or not target_id:
        print("❌ [CRITICAL] Secrets Missing!", flush=True)
        return

    print(f"💎 NODE {os.environ.get('MACHINE_NUMBER', '1')} ONLINE", flush=True)
    
    tasks = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

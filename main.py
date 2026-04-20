import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V16 CORE SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 4000    
SESSION_MAX_SEC = 250    

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"
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
                page.on("console", lambda msg: print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True))

                print(f"🔗 [{full_id}] Connecting via Fast-Commit...", flush=True)
                
                # CRITICAL: wait_until="commit" stops the 'stuck' behavior
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=45000)
                except Exception:
                    print(f"⚠️ [{full_id}] Connection slow, forcing injection anyway...", flush=True)

                # Brief pause to allow the bare minimum DOM to appear
                await asyncio.sleep(7)

                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Injection Engaged", flush=True)

                # ⚡ HYPER-SPEED INJECTION (MESSAGES + URL-JUMP NC)
                await page.evaluate("""
                    ([targetName, mDelay, nDelay, threadId]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            return `🔱 (${n}) 🌸 P R V R 🔱\\n${rail}\\n${rail}\\n🔱 (${n}) 🌸 P R V R 🔱`;
                        }

                        // 📨 MESSAGE SPAMMER
                        setInterval(() => {
                            if (window.location.href.includes('/details/')) return;
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(targetName));
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                            }
                        }, mDelay);

                        // 🛡️ NC WATCHDOG (DIRECT URL ATTACK)
                        let isProcessing = false;
                        setInterval(() => {
                            if (isProcessing) return;

                            const titleEl = document.querySelector('header span[role="link"], .x1lliihq.x193iq5w, header h1, header span');
                            const currentName = titleEl ? titleEl.innerText : "";

                            // 1. Detect mismatch and JUMP
                            if (currentName && !currentName.toLowerCase().includes(targetName.toLowerCase()) && !window.location.href.includes('/details/')) {
                                isProcessing = true;
                                console.log("🚀 NC TRIGGERED! Jumping to Details URL...");
                                window.location.href = `https://www.instagram.com/direct/t/${threadId}/details/`;
                            }

                            // 2. Details page logic
                            if (window.location.href.includes('/details/')) {
                                const input = document.querySelector('input[name="thread_name"], .x1i10hfl[type="text"]');
                                if (input && input.value !== targetName) {
                                    console.log("📝 Settings Page Ready. Forcing Name Change...");
                                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                    setter.call(input, ""); 
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    setter.call(input, targetName); 
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    
                                    setTimeout(() => {
                                        const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                                        const save = btns.find(b => /save|done|update/i.test(b.innerText)) || document.querySelector('.x1n2onr6');
                                        if (save) {
                                            console.log("🚀 SAVE CLICKED! Returning to chat...");
                                            save.click();
                                            setTimeout(() => { 
                                                window.location.href = `https://www.instagram.com/direct/t/${threadId}/`; 
                                                isProcessing = false;
                                            }, 2000);
                                        }
                                    }, 1000);
                                } else if (!input && document.readyState === 'complete') {
                                    console.log("⚠️ Input missing. Returning to chat...");
                                    window.location.href = `https://www.instagram.com/direct/t/${threadId}/`;
                                    isProcessing = false;
                                }
                            }
                        }, nDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY, target_id])

                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [{full_id}] Flushing Context...", flush=True)
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

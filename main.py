import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 CLUSTER SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 5000    
SESSION_MAX_SEC = 150    
TOTAL_DURATION = 25000   

async def check_session_validity(page, agent_id):
    """Hard exit if Instagram redirects to login (Session Expired)."""
    if "login" in page.url:
        print(f"\n❌ [{agent_id}] SESSION EXPIRED. Check your INSTA_COOKIE secret!", flush=True)
        os._exit(1)

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    start_time = asyncio.get_event_loop().time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", 
            "--disable-dev-shm-usage", 
            "--disable-gpu"
        ])
        
        while (asyncio.get_event_loop().time() - start_time) < TOTAL_DURATION:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
                    viewport={'width': 820, 'height': 1180}
                )
                
                # Cookie Extraction & Injection
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                print(f"🔗 [{full_id}] Connecting to Thread: {target_id}", flush=True)
                
                # Navigation (DOM loaded is enough for JS injection)
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=60000)
                await check_session_validity(page, full_id)

                print(f"🔥 [{full_id}] ACTIVE | Pulse: {PULSE_DELAY}ms | Watchdog: {target_name}", flush=True)

                # ⚡ HYPER-SPEED JAVASCRIPT INJECTION
                await page.evaluate("""
                    ([name, msgDelay, ncDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            let lines = [`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`];
                            for(let i=0; i<25; i++) lines.push(rail);
                            lines.push(`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`);
                            return lines.join('\\n');
                        }

                        // 📨 SPAMMER ENGINE
                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(name));
                                const enter = new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 });
                                box.dispatchEvent(enter);
                                setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                            }
                        }, msgDelay);

                        // 🛡️ NC WATCHDOG (SAVE BUTTON OPTIMIZED)
                        setInterval(() => {
                            const header = document.querySelector('header');
                            if (header && !header.innerText.toLowerCase().includes(name.toLowerCase())) {
                                const clickable = header.querySelector('span, div[role="button"], img');
                                if (clickable) {
                                    clickable.click(); // Open Chat Settings

                                    setTimeout(() => {
                                        const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"]');
                                        if (input) {
                                            input.focus();
                                            // Force React state update
                                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                            setter.call(input, ""); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            setter.call(input, name); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            input.dispatchEvent(new Event('change', { bubbles: true }));

                                            setTimeout(() => {
                                                const btns = Array.from(document.querySelectorAll('button, div[role="button"], span[role="button"]'));
                                                
                                                // 🔍 Search Strategy: 'Save' priority -> 'Done' -> Primary Class
                                                let actionBtn = btns.find(b => {
                                                    const t = b.innerText.toLowerCase();
                                                    return t.includes("save") || t.includes("done");
                                                });

                                                // Fallback to primary blue button class if text isn't found
                                                if (!actionBtn) {
                                                    actionBtn = btns.find(b => b.classList.contains('_acan') || b.classList.contains('_acap'));
                                                }

                                                if (actionBtn) {
                                                    actionBtn.click();
                                                    // Double-tap safety
                                                    setTimeout(() => { if(document.body.contains(actionBtn)) actionBtn.click(); }, 300);
                                                }
                                            }, 1000);
                                        }
                                    }, 2000); 
                                }
                            }
                        }, ncDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [{full_id}] Cycle end. Restarting...", flush=True)
                await context.close()
                gc.collect()
                
            except Exception as e:
                print(f"⚠️ [{full_id}] Error: {e}", flush=True)
                await asyncio.sleep(10)
        
        await browser.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")

    if not cookie or not target_id:
        print("❌ [CRITICAL] Missing Environment Secrets!", flush=True)
        return

    print(f"💎 NODE {os.environ.get('MACHINE_NUMBER', '1')} ONLINE", flush=True)
    
    tasks = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

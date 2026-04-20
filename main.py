import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 CLUSTER SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
NC_CHECK_DELAY = 3000    # Faster check (3s)
SESSION_MAX_SEC = 200    
TOTAL_DURATION = 25000   

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
                print(f"🔗 [{full_id}] Attempting Connection...", flush=True)
                
                # 'commit' is the fastest load state - triggers as soon as data starts arriving
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=60000)
                
                # Check for login redirect
                if "login" in page.url:
                    print(f"❌ [{full_id}] Cookie Dead!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Injection Started", flush=True)

                await page.evaluate("""
                    ([targetName, mDelay, nDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                            let lines = [`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`];
                            for(let i=0; i<25; i++) lines.push(rail);
                            lines.push(`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`);
                            return lines.join('\\n');
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

                        // 🛡️ NAME CHANGE WATCHDOG
                        setInterval(() => {
                            const header = document.querySelector('header');
                            if (header && !header.innerText.toLowerCase().includes(targetName.toLowerCase())) {
                                // Click the 'i' button or the header name
                                const infoBtn = document.querySelector('header div[role="button"], header svg[aria-label*="Details"], header span');
                                if (infoBtn) {
                                    infoBtn.click();
                                    
                                    setTimeout(() => {
                                        const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"]');
                                        if (input) {
                                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                            setter.call(input, ""); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            setter.call(input, targetName); 
                                            input.dispatchEvent(new Event('input', { bubbles: true }));
                                            
                                            setTimeout(() => {
                                                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                                                const save = btns.find(b => /save|done/i.test(b.innerText)) || document.querySelector('._acan, ._acap');
                                                if (save) {
                                                    save.click();
                                                }
                                            }, 500);
                                        }
                                    }, 1500);
                                }
                            }
                        }, nDelay);
                    }
                """, [target_name, PULSE_DELAY, NC_CHECK_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Restarting: {e}", flush=True)
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

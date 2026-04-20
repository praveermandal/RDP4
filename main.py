import os, asyncio, re, sys, subprocess

# --- 🛠️ AUTO-INSTALLER (BOOTSTRAP) ---
def bootstrap():
    print("🛠️ Starting System Bootstrap...")
    try:
        import playwright
    except ImportError:
        print("📦 Playwright not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    
    print("🌐 Installing Chromium and Linux Dependencies...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    # install-deps is required for Linux/GitHub runners to handle system libraries
    subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])
    print("✅ System Ready!")

# Run bootstrap before anything else
bootstrap()

from playwright.async_api import async_playwright

# --- ⚙️ V100 SETTINGS ---
AGENTS = 2               
PULSE_DELAY = 100        
NC_CHECK_DELAY = 5000    
SESSION_MAX_SEC = 120    
TOTAL_DURATION = 25000   

async def check_session_validity(page):
    """Stops the action if the session ID is expired or invalid."""
    if "login" in page.url:
        print("❌ [CRITICAL] Session ID Expired or Invalid! Stopping Action...")
        os._exit(1) # Hard exit to stop GitHub runner immediately

async def run_agent(agent_id, cookie, target_id, target_name):
    start_time = asyncio.get_event_loop().time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        
        while (asyncio.get_event_loop().time() - start_time) < TOTAL_DURATION:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)",
                    viewport={'width': 820, 'height': 1180}
                )
                
                sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                print(f"🔗 [Agent {agent_id}] Connecting to Thread: {target_id}...")
                
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="networkidle")
                
                # Check if we got redirected to login
                await check_session_validity(page)

                print(f"🔥 [Agent {agent_id}] Status: ACTIVE | Target: {target_name} | Speed: {PULSE_DELAY}ms")

                await page.evaluate("""
                    const targetName = arguments[0];
                    const msgDelay = arguments[1];
                    const ncDelay = arguments[2];

                    function getBlock(n) {
                        const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                        let lines = [`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`];
                        for(let i=0; i<25; i++) lines.push(rail);
                        lines.push(`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`);
                        return lines.join('\\n');
                    }

                    // SPAMMER ENGINE
                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            box.focus();
                            document.execCommand('insertText', false, getBlock(targetName));
                            box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                            setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                        }
                    }, msgDelay);

                    // NC WATCHDOG ENGINE
                    setInterval(() => {
                        const header = document.querySelector('header');
                        if (header && !header.innerText.includes(targetName)) {
                            const clickable = header.querySelector('span, div[role="button"]');
                            if (clickable) {
                                clickable.click();
                                setTimeout(() => {
                                    const input = document.querySelector('input[name="thread_name"]');
                                    if (input) {
                                        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        setter.call(input, targetName);
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        setTimeout(() => {
                                            const done = Array.from(document.querySelectorAll('button')).find(b => /Done|Save/.test(b.innerText));
                                            if (done) done.click();
                                        }, 500);
                                    }
                                }, 1200);
                            }
                        }
                    }, ncDelay);
                """, target_name, PULSE_DELAY, NC_CHECK_DELAY)

                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [Agent {agent_id}] Cycle Complete. Flushing RAM...")
                await context.close()
                
            except Exception as e:
                print(f"⚠️ [Agent {agent_id}] Error: {e}")
                await asyncio.sleep(5)
        
        await browser.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")

    if not cookie:
        print("❌ ERROR: INSTA_COOKIE not found in Secrets!")
        return

    print(f"💎 STARTING V100 MULTI-AGENT SYSTEM...")
    tasks = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

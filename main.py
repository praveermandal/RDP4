import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 SETTINGS ---
AGENTS = 2               
PULSE_DELAY = 100        
NC_CHECK_DELAY = 5000    
SESSION_MAX_SEC = 120    
TOTAL_DURATION = 25000   

async def check_session_validity(page):
    if "login" in page.url:
        print("\n❌ [CRITICAL] Session ID Expired! Stopping Action...")
        os._exit(1)

async def run_agent(agent_id, cookie, target_id, target_name):
    start_time = asyncio.get_event_loop().time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        
        while (asyncio.get_event_loop().time() - start_time) < TOTAL_DURATION:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
                    viewport={'width': 820, 'height': 1180}
                )
                
                sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                print(f"🔗 [Agent {agent_id}] Navigating to Thread...")
                
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=60000)
                await check_session_validity(page)

                print(f"🔥 [Agent {agent_id}] ACTIVE | Pulse: {PULSE_DELAY}ms")

                await page.evaluate("""
                    const targetName = arguments[0];
                    const msgDelay = arguments[1];

                    function getBlock(n) {
                        const rail = "╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿╿"; 
                        let lines = [`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`];
                        for(let i=0; i<25; i++) lines.push(rail);
                        lines.push(`🔱 (${n}) 🌸 P R V R पापा से CUD 🔱`);
                        return lines.join('\\n');
                    }

                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            box.focus();
                            document.execCommand('insertText', false, getBlock(targetName));
                            const enter = new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 });
                            box.dispatchEvent(enter);
                            setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                        }
                    }, msgDelay);
                """, target_name, PULSE_DELAY)

                await asyncio.sleep(SESSION_MAX_SEC)
                await context.close()
                
            except Exception as e:
                print(f"⚠️ [Agent {agent_id}] Error: {e}")
                await asyncio.sleep(10)
        
        await browser.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")

    if not cookie or not target_id:
        print("❌ Missing Secrets in GitHub!")
        return

    print(f"💎 V100 CORE LOADED | Agents: {AGENTS}")
    tasks = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V17 PURE SPAM SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        # 100ms between messages
SESSION_MAX_SEC = 300    # Reset RAM every 5 minutes

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
                # Mirror logs
                page.on("console", lambda msg: print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True))

                print(f"🔗 [{full_id}] Connecting...", flush=True)
                
                # Bypassing the hang with 'commit'
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=45000)
                except Exception:
                    pass

                # Wait for the chat box to actually exist
                await asyncio.sleep(8)

                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Pure Spam Mode", flush=True)

                # ⚡ HYPER-SPEED MESSAGE INJECTION
                await page.evaluate("""
                    ([targetName, mDelay]) => {
                        function getBlock(n) {
                            const rail = "╿╿╿╿╿╿╿╿"; 
                            return `🔱 (${n}) 🌸 P R V R 🔱\\n${rail}\\n${rail}\\n🔱 (${n}) 🌸 P R V R 🔱`;
                        }

                        // 📨 MESSAGE SPAMMER
                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, getBlock(targetName));
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                                
                                // Quick clear for React stabilization
                                setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                            }
                        }, mDelay);
                    }
                """, [target_name, PULSE_DELAY])

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

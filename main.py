import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V26 HIGH-SPEED SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        # Selenium-matching speed
SESSION_MAX_SEC = 21600  # 6 Hours

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
        # Optimization: Use fixed flags to reduce browser overhead
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", 
            "--js-flags='--max-old-space-size=512'"
        ])
        
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

                # Silence logs to save CPU cycles
                page.on("console", lambda msg: None) 

                print(f"🔗 [{full_id}] Connecting...", flush=True)
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=30000)
                except: pass

                await asyncio.sleep(7)
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Internal-Burner Engaged", flush=True)

                # ⚡ PURE JAVASCRIPT LOOP (No Python Overhead)
                await page.evaluate("""
                    ([tName, mDelay]) => {
                        const lightning = "      ⚡\\n        ⚡\\n          ⚡\\n        ⚡\\n      ⚡\\n".repeat(3);
                        const border = "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓";
                        const line = "◢◤ ─────────────────── ◢◤";
                        
                        const vars = [
                            `🔱👑 (${tName}) 🌸 P R V R पापा से CUD 👑🔱\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔱👑 (${tName}) 🌸 P R V R पापा से CUD 👑🔱`,
                            `💀 [${tName}] P R V R DADDY IS HERE 💀\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💀 [${tName}] P R V R DADDY IS HERE 💀`,
                            `🔥 (${tName}) बोल P R V R पापा ON TOP 🔥\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔥 (${tName}) बोल P R V R पापा ON TOP 🔥`,
                            `🥶 [${tName}] TERA SYSTEM HANG 🥶\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🥶 [${tName}] TERA SYSTEM HANG 🥶`,
                            `💢 [${tName}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💢 [${tName}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢`,
                            `🔪 [${tName}] CHUP REH RΔNDI KE 🔪\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔪 [${tName}] CHUP REH RΔNDI KE 🔪`
                        ];

                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                const msg = vars[Math.floor(Math.random() * vars.length)];
                                // Use Direct DOM Injection - much faster than typing
                                document.execCommand('insertText', false, msg);
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                                
                                // Micro-cleanup to prevent UI lag
                                if(box.innerText.length > 50) box.innerHTML = "";
                            }
                        }, mDelay);
                    }
                """, [target_name, PULSE_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Error: {e}")
                await asyncio.sleep(10)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    print(f"💎 NODE {os.environ.get('MACHINE_NUMBER', '1')} ONLINE", flush=True)
    await asyncio.gather(*[run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)])

if __name__ == "__main__":
    asyncio.run(main())

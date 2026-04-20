import os, asyncio, re, sys, gc, random
from playwright.async_api import async_playwright

# --- ⚙️ V25 CHAOS SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        # Reverted to 100ms for full-throttle chaos
SESSION_MAX_SEC = 21600  # 6 Hours per cycle

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
                
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()

                def log_filter(msg):
                    txt = msg.text.lower()
                    ignore = ["content security policy", "permissions-policy", "selfxss", "bluetooth", "unload", "webassembly", "stop!", "browser feature", "scam"]
                    if not any(x in txt for x in ignore):
                        print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True)

                page.on("console", log_filter)

                print(f"🔗 [{full_id}] Connecting...", flush=True)
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=45000)
                except: pass

                await asyncio.sleep(8)
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Chaos-Overdrive Engaged", flush=True)

                await page.evaluate("""
                    ([targetName, mDelay]) => {
                        const lightning = "      ⚡\\n        ⚡\\n          ⚡\\n        ⚡\\n      ⚡\\n".repeat(3);
                        const border = "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓";
                        const line = "◢◤ ─────────────────── ◢◤";
                        
                        const variations = [
                            (n) => `🔱👑 (${n}) 🌸 P R V R पापा से CUD 👑🔱\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔱👑 (${n}) 🌸 P R V R पापा से CUD 👑🔱`,
                            (n) => `💀 [${n}] P R V R DADDY IS HERE 💀\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💀 [${n}] P R V R DADDY IS HERE 💀`,
                            (n) => `🔥 (${n}) बोल P R V R पापा ON TOP 🔥\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔥 (${n}) बोल P R V R पापा ON TOP 🔥`,
                            (n) => `🥶 [${n}] TERA SYSTEM HANG 🥶\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🥶 [${n}] TERA SYSTEM HANG 🥶`,
                            (n) => `💢 [${n}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💢 [${n}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢`,
                            (n) => `🔪 [${n}] CHUP REH RΔNDI KE 🔪\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔪 [${n}] CHUP REH RΔNDI KE 🔪`,
                            (n) => `👺 [${n}] RΔNDI KΔ LΔDKΔ ${n} 👺\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n👺 [${n}] RΔNDI KΔ LΔDKΔ ${n} 👺`
                        ];

                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                const randomMsg = variations[Math.floor(Math.random() * variations.length)](targetName);
                                document.execCommand('insertText', false, randomMsg);
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                                setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
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
    asyncio.run(main())                    if not any(x in txt for x in ignore_list):
                        print(f"🌐 [{full_id}] Browser: {msg.text}", flush=True)

                page.on("console", log_filter)

                print(f"🔗 [{full_id}] Connecting...", flush=True)
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=45000)
                except: pass

                await asyncio.sleep(8)
                if "login" in page.url:
                    print(f"❌ [{full_id}] SESSION EXPIRED!", flush=True)
                    os._exit(1)

                print(f"🔥 [{full_id}] ACTIVE | Full-Throttle Aggression", flush=True)

                await page.evaluate("""
                    ([targetName, mDelay]) => {
                        const lightning = "      ⚡\\n        ⚡\\n          ⚡\\n        ⚡\\n      ⚡\\n".repeat(3);
                        const border = "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓";
                        const line = "◢◤ ─────────────────── ◢◤";
                        
                        const variations = [
                            (n) => `🔱👑 (${n}) 🌸 P R V R पापा से CUD 👑🔱\\n` + 
                                   `${border}\\n${line}\\n${lightning}${line}\\n${border}\\n` +
                                   `🔱👑 (${n}) 🌸 P R V R पापा से CUD 👑🔱`
                        ];

                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                const msg = variations[0](targetName);
                                document.execCommand('insertText', false, msg);
                                box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                                setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                            }
                        }, mDelay);
                    }
                """, [target_name, PULSE_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                print(f"♻️ [{full_id}] 6 Hours Completed: Refreshing Context...", flush=True)
                await context.close()
                gc.collect()

            except Exception as e:
                print(f"⚠️ [{full_id}] Error: {e}. Reconnecting...", flush=True)
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

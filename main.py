import os, asyncio, re, sys, gc, random
from playwright.async_api import async_playwright

# --- ⚙️ V21 OVERDRIVE SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
SESSION_MAX_SEC = 300    

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

                def log_filter(msg):
                    txt = msg.text.lower()
                    ignore = ["content security policy", "permissions-policy", "selfxss", "bluetooth", "unload", "webassembly", "stop!"]
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

                print(f"🔥 [{full_id}] ACTIVE | Overdrive Aggression", flush=True)

                await page.evaluate("""
                    ([targetName, mDelay]) => {
                        const variations = [
                            (n) => `💀 [${n}] P R V R DADDY IS HERE 💀\\n╿╿╿╿╿╿╿╿\\n💀 [${n}] P R V R DADDY IS HERE 💀`,
                            (n) => `🔥 (${n}) बोल P R V R पापा ON TOP 🔥\\n💠💠💠💠💠💠\\n🔥 (${n}) बोल P R V R पापा ON TOP 🔥`,
                            (n) => `🥶 [${n}] TERA SYSTEM HANG 🥶\\n🧊🧊🧊🧊🧊🧊\\n🥶 [${n}] TERA SYSTEM HANG 🥶`,
                            (n) => `🔱 (${n}) SAY 🌸 P R V R पापा🔱\\n🎀🎀🎀🎀🎀🎀\\n🔱 (${n}) SAY 🌸 P R V R पापा🔱`,
                            (n) => `💢 [${n}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢\\n⚡⚡⚡⚡⚡⚡\\n💢 [${n}] Tᴇʀɪ Mᴀ Cʜᴏᴅᴜ Mᴀᴅᴀʀᴄʜxᴅ 💢`,
                            (n) => `😈 [${n}] P R V R BAP HAI TERA 😈\\n🚩🚩🚩🚩🚩🚩\\n😈 [${n}] P R V R BAP HAI TERA 😈`,
                            (n) => `🔪 [${n}] CHUP REH RΔNDI KE 🔪\\n🩸🩸🩸🩸🩸🩸\\n🔪 [${n}] CHUP REH RΔNDI KE 🔪`,
                            (n) => `💎 (${n}) PRVR OWNS YOU BITCH 💎\\n✨✨✨✨✨✨\\n💎 (${n}) PRVR OWNS YOU BITCH 💎`,
                            (n) => `💀 [${n}] KʜᴀNDᴀN CʜᴏD DᴜɴGᴀ TᴇRᴀ 💀\\n💀💀💀💀💀💀\\n💀 [${n}] KʜᴀNDᴀN CʜᴏD DᴜɴGᴀ TᴇRᴀ 💀`,
                            (n) => `🔥 (${n}) P R V R PΔPΔ IS BACK 🔥\\n🔱🔱🔱🔱🔱🔱\\n🔥 (${n}) P R V R PΔPΔ IS BACK 🔥`,
                            (n) => `🌊 [${n}] IɴTᴇRɴᴇT Kᴀ BᴀAᴘ P R V R 🌊\\n🌊🌊🌊🌊🌊🌊\\n🌊 [${n}] IɴTᴇRɴᴇT Kᴀ BᴀAᴘ P R V R 🌊`,
                            (n) => `👺 [${n}] RΔNDI KΔ LΔDKΔ ${n} 👺\\n👹👹👹👹👹👹\\n👺 [${n}] RΔNDI KΔ LΔDKΔ ${n} 👺`
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
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    print(f"💎 NODE {os.environ.get('MACHINE_NUMBER', '1')} ONLINE", flush=True)
    await asyncio.gather(*[run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)])

if __name__ == "__main__":
    asyncio.run(main())

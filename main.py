import os, asyncio, re, sys, gc
from playwright.async_api import async_playwright

# --- ⚙️ V28 BOLD-OVERDRIVE SETTINGS ---
AGENTS_PER_MACHINE = 2   
PULSE_DELAY = 100        
SESSION_MAX_SEC = 21600  # 6 Hours

async def run_agent(agent_id, cookie, target_id, target_name):
    m_num = os.environ.get("MACHINE_NUMBER", "1")
    full_id = f"M{m_num}-A{agent_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
            "--blink-settings=imagesEnabled=false"
        ])
        
        while True:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
                )
                
                sid_match = re.search(r'sessionid=([^;]+)', cookie)
                sid = sid_match.group(1) if sid_match else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                page = await context.new_page()
                page.on("console", lambda msg: None) 

                print(f"🔗 [{full_id}] IGNITION...", flush=True)
                try:
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit")
                except: pass

                await asyncio.sleep(6)

                print(f"🔥 [{full_id}] BOLD-OVERDRIVE ACTIVE", flush=True)

                await page.evaluate("""
                    ([tName, mDelay]) => {
                        // Unicode Bold Converter
                        const toBold = (text) => {
                            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                            const boldChars = '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗';
                            return text.split('').map(c => {
                                const i = chars.indexOf(c);
                                return i > -1 ? boldChars.slice(i * 2, i * 2 + 2) : c;
                            }).join('');
                        };

                        const bName = toBold(tName);
                        const lightning = "      ⚡\\n        ⚡\\n          ⚡\\n        ⚡\\n      ⚡\\n".repeat(3);
                        const border = "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓";
                        const line = "◢◤ ─────────────────── ◢◤";
                        
                        const v = [
                            `🔱👑 (${bName}) 🌸 𝐏 𝐑 𝐕 𝐑 पापा से 𝐂𝐔𝐃 👑🔱\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔱👑 (${bName}) 🌸 𝐏 𝐑 𝐕 𝐑 पापा से 𝐂𝐔𝐃 👑🔱`,
                            `💀 [${bName}] 𝐏 𝐑 𝐕 𝐑 𝐃𝐀𝐃𝐃𝐘 𝐈𝐒 𝐇𝐄𝐑𝐄 💀\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💀 [${bName}] 𝐏 𝐑 𝐕 𝐑 𝐃𝐀𝐃𝐃𝐘 𝐈𝐒 𝐇𝐄𝐑𝐄 💀`,
                            `🔥 (${bName}) बोल 𝐏 𝐑 𝐕 𝐑 पापा 𝐎𝐍 𝐓𝐎𝐏 🔥\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔥 (${bName}) बोल 𝐏 𝐑 𝐕 𝐑 पापा 𝐎𝐍 𝐓𝐎𝐏 🔥`,
                            `🥶 [${bName}] 𝐓𝐄𝐑𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 𝐇𝐀𝐍𝐆 🥶\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🥶 [${bName}] 𝐓𝐄𝐑𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 𝐇𝐀𝐍𝐆 🥶`,
                            `💢 [${bName}] 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐇𝐎𝐃𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃 💢\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n💢 [${bName}] 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐇𝐎𝐃𝐔 𝐌𝐀𝐃𝐀𝐑𝐂𝐇𝐎𝐃 💢`,
                            `🔪 [${bName}] 𝐂𝐇𝐔𝐏 𝐑𝐄𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 🔪\\n${border}\\n${line}\\n${lightning}${line}\\n${border}\\n🔪 [${bName}] 𝐂𝐇𝐔𝐏 𝐑𝐄𝐇 𝐑𝐀𝐍𝐃𝐈 𝐊𝐄 🔪`
                        ];

                        setInterval(() => {
                            const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                            if (box) {
                                box.focus();
                                document.execCommand('insertText', false, v[Math.floor(Math.random() * v.length)]);
                                box.dispatchEvent(new KeyboardEvent('keydown', { 
                                    bubbles: true, key: 'Enter', code: 'Enter', keyCode: 13 
                                }));
                                box.innerHTML = "";
                            }
                        }, mDelay);
                    }
                """, [target_name, PULSE_DELAY])

                await asyncio.sleep(SESSION_MAX_SEC)
                await context.close()
                gc.collect()

            except Exception:
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "PRVR")
    if not cookie or not target_id: return
    print(f"🚀 V28 BOLD-OVERDRIVE ONLINE | 16 AGENTS ACTIVE", flush=True)
    await asyncio.gather(*[run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)])

if __name__ == "__main__":
    asyncio.run(main())

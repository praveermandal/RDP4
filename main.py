// 🛡️ AUTO NC WATCHDOG (FORCE TRIGGER VERSION)
setInterval(() => {
    const header = document.querySelector('header');
    // Check if header exists and name is wrong (case-insensitive check)
    if (header && !header.innerText.toLowerCase().includes(name.toLowerCase())) {
        const clickable = header.querySelector('span, div[role="button"], img');
        if (clickable) {
            clickable.click(); // Open Sidebar/Modal

            setTimeout(() => {
                const input = document.querySelector('input[name="thread_name"], input[placeholder*="Name"]');
                if (input) {
                    // 1. Force Focus and Clear
                    input.focus();
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    setter.call(input, ""); // Clear first
                    input.dispatchEvent(new Event('input', { bubbles: true }));

                    // 2. Inject Target Name
                    setter.call(input, name);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));

                    setTimeout(() => {
                        // 3. Find "Done" or "Save" button using multiple text variations
                        const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                        const done = btns.find(b => {
                            const t = b.innerText.toLowerCase();
                            return t === "done" || t === "save" || t === "save changes";
                        });

                        if (done) {
                            done.click();
                            // Optional: Click again to be sure
                            setTimeout(() => { if (document.body.contains(done)) done.click(); }, 300);
                        }
                    }, 800);
                }
            }, 1500); // Wait for modal animation
        }
    }
}, ncDelay);

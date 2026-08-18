# refresh_token.py
import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def get_fresh_token():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Navigate to playground
        print("  [Playwright] Navigating to acemusic.ai/playground...")
        await page.goto("https://acemusic.ai/playground", timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        # Try multiple selectors for the input field
        selectors = [
            "textarea",
            "textarea[placeholder*='Describe']",
            "textarea[placeholder*='styles']",
            "input[type='text']",
            "[contenteditable='true']",
            "div[role='textbox']",
            ".simple-input",
            "#simple-input",
        ]
        
        input_element = None
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    input_element = element
                    print(f"  [Playwright] Found input with selector: {selector}")
                    break
            except PlaywrightTimeoutError:
                continue
        
        if not input_element:
            await page.screenshot(path="debug_screenshot.png")
            raise Exception("Could not find input field. Screenshot saved.")
        
        # Ensure "Simple" tab is active
        try:
            simple_tab = await page.query_selector("button:has-text('Simple')")
            if simple_tab:
                await simple_tab.click()
                print("  [Playwright] Clicked 'Simple' tab")
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Fill the prompt
        await input_element.fill("romantic pop song")
        print("  [Playwright] Filled prompt")
        
        # Find and click Generate button
        generate_selectors = [
            "button:has-text('Generate')",
            "button[type='submit']",
            ".generate-btn",
            "#generate-btn",
        ]
        generate_button = None
        for sel in generate_selectors:
            try:
                btn = await page.wait_for_selector(sel, timeout=3000)
                if btn:
                    generate_button = btn
                    break
            except PlaywrightTimeoutError:
                continue
        
        if not generate_button:
            raise Exception("Could not find Generate button")
        
        await generate_button.click()
        print("  [Playwright] Clicked Generate")
        
        # Wait for release_task request and extract ai_token
        async with page.expect_request("**/release_task", timeout=30000) as request_info:
            request = await request_info.value
            post_data = await request.post_data()
            if post_data and b'ai_token' in post_data.encode():
                # Try boundary-based extraction
                content_type = request.headers.get('content-type', '')
                if 'boundary=' in content_type:
                    boundary = content_type.split('boundary=')[-1]
                    parts = post_data.split(f'--{boundary}'.encode())
                    for part in parts:
                        if b'ai_token' in part:
                            token = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode()
                            await browser.close()
                            return token
                # Fallback: regex
                match = re.search(r'name="ai_token"\s*\r\n\r\n([^\r\n]+)', post_data)
                if match:
                    token = match.group(1)
                    await browser.close()
                    return token
        
        await browser.close()
        return None

if __name__ == "__main__":
    token = asyncio.run(get_fresh_token())
    if token:
        print(token)
    else:
        print("ERROR: Could not fetch token")
        exit(1)

# refresh_token.py
import os
import asyncio
import requests
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

def get_token_via_api_key():
    """Try to get a fresh token using the ACE_MUSIC_API_KEY directly."""
    api_key = os.environ.get("ACE_MUSIC_API_KEY")
    if not api_key:
        return None

    # Try different authentication methods
    base_url = "https://acem-api.acemusic.ai/api/acem/user/ai/token"
    
    auth_methods = [
        {"headers": {"Authorization": f"Bearer {api_key}"}},
        {"headers": {"X-API-Key": api_key}},
        {"headers": {"Api-Key": api_key}},
        {"params": {"api_key": api_key}},
        {"params": {"key": api_key}},
    ]
    
    for method in auth_methods:
        try:
            if "headers" in method:
                resp = requests.get(base_url, headers=method["headers"], timeout=10)
            else:
                resp = requests.get(base_url, params=method["params"], timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("token") or data.get("data", {}).get("token")
                if token:
                    print("  [Token] Obtained via API key")
                    return token
        except:
            continue
    return None

async def get_fresh_token_playwright():
    """Fallback: use Playwright to capture token from browser."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("  [Playwright] Navigating to acemusic.ai/playground...")
        await page.goto("https://acemusic.ai/playground", timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        # Dump page HTML for debugging (if needed)
        html = await page.content()
        with open("page_debug.html", "w") as f:
            f.write(html)
        
        # Try to find input using various selectors
        selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "div[role='textbox']",
            ".simple-input",
            "#simple-input",
            "input[placeholder*='Describe']",
            "textarea[placeholder*='Describe']",
        ]
        
        input_element = None
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    input_element = element
                    print(f"  [Playwright] Found input with: {selector}")
                    break
            except PlaywrightTimeoutError:
                continue
        
        if not input_element:
            # Try to find any input using XPath
            try:
                element = await page.wait_for_selector("//input | //textarea", timeout=5000)
                if element:
                    input_element = element
                    print("  [Playwright] Found input via XPath")
            except:
                pass
        
        if not input_element:
            await page.screenshot(path="debug_screenshot.png")
            raise Exception("Could not find input field. Screenshot saved.")
        
        # Click "Simple" tab if present
        try:
            simple_tab = await page.query_selector("button:has-text('Simple')")
            if simple_tab:
                await simple_tab.click()
                print("  [Playwright] Clicked 'Simple' tab")
                await page.wait_for_timeout(1000)
        except:
            pass
        
        await input_element.fill("romantic pop song")
        print("  [Playwright] Filled prompt")
        
        # Click Generate
        generate_btn = None
        for sel in ["button:has-text('Generate')", "button[type='submit']", ".generate-btn"]:
            try:
                btn = await page.wait_for_selector(sel, timeout=3000)
                if btn:
                    generate_btn = btn
                    break
            except:
                continue
        if not generate_btn:
            raise Exception("Could not find Generate button")
        
        await generate_btn.click()
        print("  [Playwright] Clicked Generate")
        
        # Capture release_task request
        async with page.expect_request("**/release_task", timeout=30000) as request_info:
            request = await request_info.value
            post_data = await request.post_data()
            if post_data and b'ai_token' in post_data.encode():
                # Extract token
                content_type = request.headers.get('content-type', '')
                if 'boundary=' in content_type:
                    boundary = content_type.split('boundary=')[-1]
                    parts = post_data.split(f'--{boundary}'.encode())
                    for part in parts:
                        if b'ai_token' in part:
                            token = part.split(b'\r\n\r\n')[1].split(b'\r\n')[0].decode()
                            await browser.close()
                            return token
                # Fallback regex
                match = re.search(r'name="ai_token"\s*\r\n\r\n([^\r\n]+)', post_data)
                if match:
                    token = match.group(1)
                    await browser.close()
                    return token
        
        await browser.close()
        return None

async def get_fresh_token():
    """Main: try API key first, then Playwright."""
    # 1. Try API key
    token = get_token_via_api_key()
    if token:
        return token
    
    # 2. Fallback to Playwright
    print("  [Token] API key method failed, using Playwright...")
    return await get_fresh_token_playwright()

if __name__ == "__main__":
    token = asyncio.run(get_fresh_token())
    if token:
        print(token)
    else:
        print("ERROR: Could not fetch token")
        exit(1)

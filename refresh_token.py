# refresh_token.py
import asyncio
from playwright.async_api import async_playwright

async def get_fresh_token():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to playground
        await page.goto("https://acemusic.ai/playground", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Enter a prompt to trigger generation
        await page.fill("textarea", "romantic pop song")
        await page.click("button:has-text('Generate')")
        
        # Capture the release_task request
        async with page.expect_request("**/release_task") as request_info:
            request = await request_info.value
            post_data = await request.post_data()
            if post_data and b'ai_token' in post_data.encode():
                # Extract ai_token from multipart form data
                parts = post_data.split('--')
                for part in parts:
                    if 'ai_token' in part:
                        token = part.split('\r\n\r\n')[1].split('\r\n')[0]
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

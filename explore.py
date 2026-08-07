import asyncio
import os
import json
from playwright.async_api import async_playwright

async def explore():
    print("Starting Playwright exploration...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Listen to network requests to trace APIs if any
        page.on("response", lambda response: print(f"Response: {response.status} {response.url}"))

        print("Navigating to https://impds.nic.in/sale/")
        await page.goto("https://impds.nic.in/sale/", wait_until="networkidle", timeout=60000)
        
        title = await page.title()
        print(f"Page Title: {title}")

        # Save HTML for inspection
        content = await page.content()
        with open("./page_home.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved page_home.html")

        await page.screenshot(path="./home.png")
        print("Saved home.png screenshot")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore())

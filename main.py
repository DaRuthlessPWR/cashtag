from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.async_api import async_playwright
import asyncio
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BROWSERLESS_WS = os.getenv("BROWSERLESS_WS")  # set in Railway

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    url = f"https://cash.app/${tag}"

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSERLESS_WS)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=15000)

        try:
            name = await page.locator('[data-testid="profile-name"]').inner_text()
            profile_pic = await page.locator('img[alt="profile"]').get_attribute('src')
        except:
            return {"error": "Profile not found or changed"}

        return {
            "name": name,
            "cashtag": f"${tag}",
            "profile_picture": profile_pic,
        }

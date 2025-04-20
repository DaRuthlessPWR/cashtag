from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import logging

app = FastAPI()

# Allow all CORS origins (safe for dev, restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    url = f"https://cash.app/${tag}"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, timeout=30000)
            await page.wait_for_selector("h2.css-1dp5vir", timeout=10000)

            name = await page.inner_text("h2.css-1dp5vir")
            cashtag = await page.inner_text("div.css-1f8nq3s")
            img = await page.get_attribute("img[alt='Profile photo']", "src")

            await browser.close()

            return {
                "name": name,
                "cashtag": cashtag,
                "profile_picture": img
            }

    except PlaywrightTimeoutError:
        return {"error": f"Timeout waiting for page for ${tag}"}
    except Exception as e:
        return {"error": f"Cashtag ${tag} not found or blocked. Detail: {str(e)}"}

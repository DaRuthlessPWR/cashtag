from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from playwright.async_api import async_playwright

app = FastAPI()

# CORS for FlutterFlow
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
async def get_cashtag_info(tag: Optional[str] = Query(None)):
    if not tag:
        return {"error": "No tag provided"}

    ws_endpoint = os.getenv("BROWSERLESS_WS")
    if not ws_endpoint:
        return {"error": "Browserless WebSocket URL not set"}

    url = f"https://cash.app/{tag}"

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")

        try:
            name = await page.inner_text("h2.css-1dp5vir")
            img = await page.get_attribute("img[alt*='Profile']", "src")
            cashtag = await page.inner_text("div.css-18suhml span")

            return {
                "name": name,
                "cashtag": cashtag,
                "profile_picture": img
            }
        except Exception as e:
            return {"error": f"Failed to scrape: {str(e)}"}
        finally:
            await browser.close()

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.async_api import async_playwright
import logging

app = FastAPI()

# Enable CORS for FlutterFlow or any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

async def scrape_profile(tag: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = f"https://cash.app/${tag}"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)

            # Grab name and image from OpenGraph meta tags
            name = await page.get_attribute('meta[property="og:title"]', 'content')
            profile_picture = await page.get_attribute('meta[property="og:image"]', 'content')

            if not name or not profile_picture:
                return {"error": "Cashtag not found or missing profile info."}

            return {
                "name": name,
                "cashtag": f"${tag}",
                "profile_picture": profile_picture
            }

        except Exception as e:
            logging.exception("Scraping failed")
            return {"error": f"Scraping failed: {str(e)}"}

        finally:
            await browser.close()

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = Query(..., min_length=1)):
    if not tag:
        return {"error": "No tag provided"}
    return await scrape_profile(tag)

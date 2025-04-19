from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import logging

app = FastAPI()

# Allow all origins — restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

async def scrape_cashtag(tag: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = f"https://cash.app/${tag}"

        try:
            await page.goto(url, timeout=15000)

            name = await page.get_attribute('meta[property="og:title"]', 'content')
            profile_picture = await page.get_attribute('meta[property="og:image"]', 'content')

            if not name or not profile_picture:
                return {"error": "Missing info or invalid cashtag."}

            return {
                "name": name,
                "cashtag": f"${tag}",
                "profile_picture": profile_picture
            }

        except Exception as e:
            logging.exception("Scraping failed")
            return {"error": str(e)}

        finally:
            await browser.close()

@app.get("/cashtag")
async def get_cashtag_info(tag: str = Query(..., min_length=1)):
    return await scrape_cashtag(tag)

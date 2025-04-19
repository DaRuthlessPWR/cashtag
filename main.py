from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.async_api import async_playwright

app = FastAPI()

# Allow FlutterFlow (and all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

async def scrape_profile(tag: str) -> dict:
    """
    Scrape the Cash App profile info for a single cashtag.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = f"https://cash.app/${tag}"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)

            # Look for required meta tags
            name = await page.get_attribute('meta[property="og:title"]', 'content')
            profile_picture = await page.get_attribute('meta[property="og:image"]', 'content')

            if name and profile_picture:
                return {
                    "name": name,
                    "cashtag": f"${tag}",
                    "profile_picture": profile_picture
                }
            else:
                return {"error": "Profile not found or missing meta tags."}

        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}
        finally:
            await browser.close()

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = Query(..., min_length=1)):
    if not tag:
        return {"error": "No tag provided"}

    data = await scrape_profile(tag)

    if "error" in data:
        return {"error": data["error"]}
    
    return {"cashtag_suggestions": [data]}

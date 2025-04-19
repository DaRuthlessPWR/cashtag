from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

app = FastAPI()

# CORS setup for FlutterFlow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is live."}

@app.get("/cashtag")
def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    url = f"https://cash.app/{tag.lstrip('$')}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            name_selector = "h2[class*=css]"
            img_selector = "img[src*='/p/']"

            try:
                name = page.inner_text(name_selector, timeout=5000)
            except PlaywrightTimeout:
                name = None

            try:
                image_url = page.locator(img_selector).get_attribute("src", timeout=5000)
            except PlaywrightTimeout:
                image_url = None

            browser.close()

            if not name and not image_url:
                return {"error": f"Cashtag ${tag} not found or blocked"}

            return {
                "cashtag": f"${tag}",
                "name": name or "Unknown",
                "profile_picture": image_url or "Not available"
            }

    except Exception as e:
        return {"error": f"Failed to scrape: {str(e)}"}

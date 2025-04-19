from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

app = FastAPI()

# Allow FlutterFlow (and all origins for now)
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
def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f"https://cash.app/${tag}"
            page.goto(url, timeout=15000)  # 15s timeout

            # Wait for a visible element that always loads if the profile exists
            page.wait_for_selector('img[src^="https://cash.app/p/"]', timeout=10000)

            # Extract data
            name_element = page.query_selector('h2')  # Name
            name = name_element.inner_text().strip() if name_element else None

            profile_img = page.query_selector('img[src^="https://cash.app/p/"]')
            profile_url = profile_img.get_attribute("src") if profile_img else None

            if not name or not profile_url:
                raise Exception("Missing profile info")

            return {
                "name": name,
                "cashtag": f"${tag}",
                "profile_picture": profile_url
            }

    except PlaywrightTimeoutError:
        return {"error": f"Timeout waiting for page for ${tag}"}
    except Exception as e:
        return {"error": f"Cashtag ${tag} not found or blocked. Detail: {str(e)}"}

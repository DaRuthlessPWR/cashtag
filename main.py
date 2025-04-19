from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

app = FastAPI()

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
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle")

            # Check if page shows "not found"
            if "doesn’t exist" in page.content():
                return {"error": f"Cashtag ${tag} not found."}

            # Try known profile selectors
            name_element = page.query_selector('h2')
            name = name_element.inner_text().strip() if name_element else None

            image_element = page.query_selector('img[src^="https://cash.app/p/"]')
            profile_picture = image_element.get_attribute("src") if image_element else None

            if not name or not profile_picture:
                raise Exception("Profile data missing")

            return {
                "name": name,
                "cashtag": f"${tag}",
                "profile_picture": profile_picture
            }

    except PlaywrightTimeoutError:
        return {"error": f"Timeout waiting for page for ${tag}"}
    except Exception as e:
        return {"error": f"Cashtag ${tag} not found or blocked. Detail: {str(e)}"}

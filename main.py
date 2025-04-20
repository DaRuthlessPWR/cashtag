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

@app.get("/cashtag")
def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = f"https://cash.app/${tag}"
            page.goto(url, timeout=30000)

            # Wait until h2 appears (indicates page is interactive)
            page.wait_for_selector("h2[class^='chakra-heading']", timeout=10000)

            # Then wait a bit more just in case
            page.wait_for_timeout(2000)

            # Grab the values
            name = page.locator("h2[class^='chakra-heading']").first.text_content()
            profile_picture = page.locator("img[class^='chakra-image']").first.get_attribute("src")

            if not name or not profile_picture:
                print("DEBUG HTML ↓↓↓↓↓↓↓↓")
                print(page.content())
                print("↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
                raise Exception("Profile data missing")

            return {
                "name": name.strip(),
                "cashtag": f"${tag}",
                "profile_picture": profile_picture
            }

    except PlaywrightTimeoutError:
        return {"error": f"Timeout waiting for page for ${tag}"}
    except Exception as e:
        return {"error": f"Cashtag ${tag} not found or blocked. Detail: {str(e)}"}

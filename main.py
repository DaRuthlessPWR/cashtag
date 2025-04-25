from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/cashtag")
async def get_cashtag_info(tag: str = Query(..., min_length=1)):
    url = f"https://cash.app/${tag}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=15000)
            name = await page.inner_text('[data-testid="profile-name"]')
            img = await page.get_attribute('img[alt="profile image"]', 'src')
            await browser.close()
            return {
                "cashtag": f"${tag}",
                "name": name,
                "profile_image": img
            }
        except Exception:
            await browser.close()
            return JSONResponse(status_code=404, content={"error": "User not found or blocked scraping."})

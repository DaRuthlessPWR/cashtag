from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
from typing import Optional, List

app = FastAPI()

# Allow FlutterFlow (and all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_cashtag_suggestions(query: str) -> List[dict]:
    """
    Function to scrape and get cashtag suggestions from CashApp profiles.
    This will return real-time results based on user input.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        search_url = f"https://cash.app/{query}"
        await page.goto(search_url)

        results = []
        try:
            # Extract relevant cashtag suggestions (example: we can get meta tags or visible data)
            # This is just a placeholder for actual scraping logic
            # You can parse the page and extract relevant cashtag matches
            name = await page.get_attribute('meta[property="og:title"]', 'content')
            image = await page.get_attribute('meta[property="og:image"]', 'content')
            
            # If valid data is found
            if name and image:
                results.append({
                    "name": name,
                    "cashtag": f"${query}",
                    "profile_picture": image
                })
        except Exception as e:
            print(f"Error scraping {query}: {e}")
        finally:
            await browser.close()

        return results

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = Query(..., min_length=1)):
    if not tag:
        return {"error": "No tag provided"}

    # Get dynamic suggestions based on the tag search
    suggestions = await get_cashtag_suggestions(tag)

    if not suggestions:
        return {"error": "No suggestions found for this tag"}

    return {"cashtag_suggestions": suggestions}

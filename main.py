from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from playwright.async_api import async_playwright

app = FastAPI()

# Allow FlutterFlow (and all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def scrape_profile(tag: str) -> dict:
    """
    Scrape the Cash App profile information (name, profile picture) for the given cashtag.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Start headless browser
        page = await browser.new_page()  # Create new page

        url = f"https://cash.app/${tag}"
        await page.goto(url, wait_until="domcontentloaded")  # Wait for the page to load

        # Try to extract profile information
        try:
            # Get the profile name from the og:title meta tag
            name = await page.get_attribute('meta[property="og:title"]', 'content')
            # Get the profile picture from the og:image meta tag
            profile_picture = await page.get_attribute('meta[property="og:image"]', 'content')

            if name and profile_picture:
                return {"name": name, "cashtag": f"${tag}", "profile_picture": profile_picture}
            else:
                return {"error": "Profile information not found."}
        except Exception as e:
            print(f"Error while scraping {tag}: {e}")
            return {"error": "Failed to scrape profile."}
        finally:
            await browser.close()

# Generate variations based on the tag (e.g., tag, tag123, tag456, etc.)
def generate_variations(tag: str) -> List[str]:
    variations = [tag]  # Start with the original tag
    for i in range(1, 6):  # We will generate 5 variations (e.g., tag123, tag456, etc.)
        variations.append(f"{tag}{i}")
    return variations

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

@app.get("/cashtag")
async def get_cashtag_info(tag: Optional[str] = Query(..., min_length=1)):
    if not tag:
        return {"error": "No tag provided"}

    # Generate variations for the tag
    variations = generate_variations(tag)

    cashtag_results = []
    # Scrape data for each variation
    for var in variations:
        scraped_data = await scrape_profile(var)
        if 'error' not in scraped_data:
            cashtag_results.append(scraped_data)
    
    if cashtag_results:
        return {"cashtag_suggestions": cashtag_results}
    else:
        return {"error": "No valid profiles found for the provided cashtags."}

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain for security
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

async def scrape_cashapp_profile(tag: str):
    url = f"https://cash.app/${tag}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=HEADERS)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        name_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")
        if name_tag and image_tag:
            return {
                "name": name_tag["content"],
                "cashtag": f"${tag}",
                "profile_picture": image_tag["content"]
            }
        return None

@app.get("/cashtag")
async def search_cashtags(tag: str = Query(..., min_length=1)):
    # You can improve this to try more variations based on search term
    tags_to_try = [tag, tag + "123", tag + "99"]
    results = []
    for t in tags_to_try:
        data = await scrape_cashapp_profile(t)
        if data:
            results.append(data)
    return results

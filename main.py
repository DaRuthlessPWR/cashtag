from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow FlutterFlow (and all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this
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

    # Construct the URL for the Cashtag page (Cash App user page)
    url = f"https://cash.app/{tag}"

    try:
        # Fetch the page content
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a valid response (status code 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape the required details
        name = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else "Unknown"
        profile_picture = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None

        # Return the scraped data
        return {
            "name": name,
            "cashtag": f"${tag}",
            "profile_picture": profile_picture
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch data for cashtag '{tag}': {str(e)}"}

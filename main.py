from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

# CORS setup to allow requests from FlutterFlow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing (set specific domain in production)
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

    # Example mock data, replace this with real scraping logic if needed
    return {
        "name": "John Doe",
        "cashtag": f"${tag}",
        "profile_picture": f"https://cash.app/p/{tag}.jpg"
    }

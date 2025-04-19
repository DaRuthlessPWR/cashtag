from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

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

    # Mock data (replace this with actual scraping if needed)
    return {
        "name": "John Doe",
        "cashtag": f"${tag}",
        "profile_picture": f"https://cash.app/p/{tag}.jpg"
    }

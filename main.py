from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {"message": "Cashtag Grabber API is running."}

# Function to generate variations of a cashtag
def generate_variations(tag: str) -> List[str]:
    variations = [tag]  # Start with the original tag
    # Generate number-based variations
    for i in range(1, 6):  # We will generate 5 variations (e.g., tag123, tag234, etc.)
        variations.append(f"{tag}{i}")
    return variations

@app.get("/cashtag")
def get_cashtag_info(tag: Optional[str] = None):
    if not tag:
        return {"error": "No tag provided"}

    # Generate variations for the tag
    variations = generate_variations(tag)

    # Mock data for each variation (replace with actual scraping if needed)
    cashtag_results = []
    for var in variations:
        cashtag_results.append({
            "name": f"User for {var}",  # You would replace this with real name from scraping
            "cashtag": f"${var}",
            "profile_picture": f"https://cash.app/p/{var}.jpg"  # Placeholder PFP URL
        })
    
    return {"cashtag_suggestions": cashtag_results}

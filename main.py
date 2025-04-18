from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

class CashtagInfo(BaseModel):
    name: str
    cashtag: str
    profile_picture: str

@app.get("/cashtag/{tag}", response_model=CashtagInfo)
async def get_cashtag_info(tag: str):
    url = f"https://cash.app/${tag}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Cashtag not found")

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        name = soup.find("meta", {"property": "og:title"})["content"]
        image = soup.find("meta", {"property": "og:image"})["content"]
        return CashtagInfo(
            name=name,
            cashtag=f"${tag}",
            profile_picture=image
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Could not parse profile")

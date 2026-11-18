import requests
from fastapi import APIRouter

from app.config import config

router = APIRouter(prefix="/water", tags=["Water"])

@router.get("/quota")
def get_textbelt_quota():
    response = requests.get(
        f"https://textbelt.com/quota/{config.textbelt_api_key}",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    if not data["success"]:
        raise RuntimeError("Failed to retrieve quota")

    return {"texts_remaining": data["quotaRemaining"]}
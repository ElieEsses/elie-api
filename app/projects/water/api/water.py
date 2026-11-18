import requests
from fastapi import APIRouter, Depends

from app.config import config
from app.projects.water.models.models import TextQuotaResponse
from app.shared.auth import get_current_user_id

router = APIRouter(prefix="/water", tags=["Water"])

router = APIRouter(prefix="/water", tags=["Water"])


@router.get(
    "/quota",
    response_model=TextQuotaResponse,
    dependencies=[Depends(get_current_user_id)],
)
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

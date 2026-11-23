from fastapi import APIRouter, Depends, HTTPException

from app.config import config
from app.projects.water.models.models import TextQuotaResponse, TextResponse
from app.projects.water.services.water_text_utils import (
    get_textbelt_quota,
    send_message,
    send_water_reminder,
)
from app.shared.auth import get_current_user_id, verify_internal_api_key

router = APIRouter(prefix="/water", tags=["Water Reminders"])


@router.get(
    "/quota",
    response_model=TextQuotaResponse,
    dependencies=[Depends(get_current_user_id)],
)
def get_quota():
    """
    Get the remaining text message quota from Textbelt.
    """
    try:
        quota_remaining = get_textbelt_quota()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve quota")

    return TextQuotaResponse(textbelt_quota_remaining=quota_remaining)


@router.post(
    "/send-message",
    response_model=TextResponse,
    dependencies=[Depends(get_current_user_id)],
)
def send_message_endpoint():
    """
    Sends a water reminder message using Textbelt API.
    """
    return send_message()


@router.post(
    "/internal/send-message",
    response_model=TextResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def internal_send_message():
    """
    Internal endpoint (with internal API verification) to send water reminder message using Textbelt API.
    """
    return send_message()


@router.post(
    "/send-custom-message",
    response_model=TextResponse,
    dependencies=[Depends(get_current_user_id)],
)
def send_custom_message(message_body: str):
    """
    Sends a custom water message using Textbelt API.
    """
    to_number = (
        config.elie_number
        if config.texting_service_mode == "dev"
        else config.helaina_number
    )

    try:
        quota_remaining = send_water_reminder(to_number, message_body)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send message")

    return TextResponse(
        message_sent=message_body,
        recipient="Elie" if config.env == "dev" else "Helaina",
        recipient_number=to_number,
        remaining_quota=quota_remaining,
    )

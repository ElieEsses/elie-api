import logging
from random import choice

import requests

from app.config import config
from app.projects.water.models.models import TextResponse
from app.projects.water.services.message_lists import (
    greetings,
    love_emojis,
    messages,
    water_emojis,
)

logger = logging.getLogger(__name__)


def get_textbelt_quota() -> int:
    response = requests.get(
        f"https://textbelt.com/quota/{config.textbelt_api_key}",
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    if not data["success"]:
        logger.error("Failed to retrieve quota")
        raise RuntimeError("Failed to retrieve quota")

    quota_remaining = data.get("quotaRemaining")
    return quota_remaining


def generate_message():
    for _ in range(10):
        message = (
            f"{choice(greetings)} "
            f"{choice(messages)} "
            f"{choice(water_emojis)}{choice(love_emojis)}"
        )

        if len(message.encode("utf-16-le")) // 2 <= 70:
            return message

    raise RuntimeError(
        "Failed to generate a message within the character limit after 10 attempts."
    )


def send_water_reminder(to_number: str, message_body: str) -> int:
    resp = requests.post(
        "https://textbelt.com/text",
        data={
            "phone": to_number,
            "message": message_body,
            "key": config.textbelt_api_key,
        },
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()

    if not result.get("success"):
        logger.error(f"Failed to send message: {result.get('error')}")
        raise RuntimeError(result.get("error", "SMS request failed"))

    quota_remaining = result["quotaRemaining"]
    return quota_remaining


def send_message() -> TextResponse:
    to_number = (
        config.elie_number
        if config.texting_service_mode == "dev"
        else config.helaina_number
    )
    recipient_name = "Elie" if config.texting_service_mode == "dev" else "Helaina"

    message_body = generate_message()

    quota_remaining = send_water_reminder(to_number, message_body)
    logger.info(
        f"Text sent to {recipient_name}: {message_body} (Quota remaining: {quota_remaining})"
    )

    return TextResponse(
        message_sent=message_body,
        recipient=recipient_name,
        recipient_number=to_number,
        remaining_quota=quota_remaining,
    )

from pydantic import BaseModel


class TextQuotaResponse(BaseModel):
    textbelt_quota_remaining: int


class TextResponse(BaseModel):
    message_sent: str
    recipient: str
    recipient_number: str
    remaining_quota: int

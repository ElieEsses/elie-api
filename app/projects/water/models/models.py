from pydantic import BaseModel


class TextQuotaResponse(BaseModel):
    texts_remaining: int

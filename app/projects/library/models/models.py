from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BookData(BaseModel):
    isbn: str | None = None
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    first_publish_year: int | None = None
    num_pages: int | None = None
    cover_url: str | None = None


class BookResponse(BaseModel):
    id: int
    isbn: str
    title: str
    authors: list[str]
    first_publish_year: int | None
    num_pages: int | None
    cover_url: str | None
    status: str
    pages_read: int
    nfc_url: str | None = None
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ReadingProgressUpdate(BaseModel):
    status: Literal["unread", "reading", "finished"] | None = None
    pages_read: int | None = Field(default=None, ge=0)
    rating: float | None = Field(default=None, ge=0, le=5)


class NoteCreate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

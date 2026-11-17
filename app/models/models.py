from typing import Literal
from uuid import UUID
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

    model_config = ConfigDict(from_attributes=True)

class BookDetailResponse(BookResponse):
    status: str
    pages_read: int
    nfc_url: str | None = None

class ReadingProgressUpdate(BaseModel):
    status: Literal["unread", "reading", "finished"] | None = None
    pages_read: int | None = Field(default=None, ge=0)

class LibraryEntryResponse(BaseModel):
    user_id: UUID
    book_id: int
    status: str
    pages_read: int
    nfc_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
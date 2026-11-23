from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: Literal["dev", "prod"] = "dev"

    internal_api_key: str

    frontend_url: str

    google_api_key: str
    google_books_url: str = "https://www.googleapis.com/books/v1/volumes"

    open_library_base_url: str = "https://openlibrary.org"
    open_library_cover_url: str = "https://covers.openlibrary.org"

    db_connection_string: str
    db_url: str
    db_publishable_key: str

    textbelt_api_key: str
    elie_number: str
    helaina_number: str
    texting_service_mode: Literal["dev", "prod"] = "dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Settings()  # pyright: ignore[reportCallIssue]

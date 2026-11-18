from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"

    frontend_url: str

    google_api_key: str
    google_books_url: str = "https://www.googleapis.com/books/v1/volumes"

    open_library_base_url: str = "https://openlibrary.org"
    open_library_cover_url: str = "https://covers.openlibrary.org"

    db_connection_string: str
    db_url: str
    db_publishable_key: str

    textbelt_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Settings()  # pyright: ignore[reportCallIssue]

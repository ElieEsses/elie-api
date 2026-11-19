from requests import RequestException
from requests import get as requests_get

from app.config import config
from app.projects.library.models.models import BookData


def get_book_data(isbn: str) -> BookData | None:
    # remove - from isbn and strip whitespace
    isbn = isbn.replace("-", "").strip()

    # get title, authors, page count from google books api
    try:
        response = requests_get(
            config.google_books_url,
            params={"q": f"isbn:{isbn}", "key": config.google_api_key, "maxResults": 5},
            timeout=10,
        )
        response.raise_for_status()
    except RequestException as e:
        raise RuntimeError("Google Books lookup failed.") from e

    items = response.json().get("items", [])

    # if no items are returned, return None
    if not items:
        return None

    data = items[0].get("volumeInfo", {})

    title = data.get("title")
    authors = data.get("authors", [])
    page_count = data.get("pageCount")

    # get first publish year from open library api
    metadata_url = f"{config.open_library_base_url}/search.json"
    # sets first_publish_year to None if not found
    first_publish_year = None
    try:
        metadata_res = requests_get(
            metadata_url,
            params={"isbn": isbn, "fields": "first_publish_year", "limit": 1},
            timeout=10,
        )
        metadata_res.raise_for_status()

        docs = metadata_res.json().get("docs", [])
        if docs:
            first_publish_year = docs[0].get("first_publish_year") if docs else None

    except RequestException:
        pass

    # cover image url open library api
    cover_url = f"{config.open_library_cover_url}/b/isbn/{isbn}-L.jpg?default=false"

    return BookData(
        isbn=isbn,
        title=title,
        authors=authors,
        first_publish_year=first_publish_year,
        num_pages=page_count,
        cover_url=cover_url,
    )

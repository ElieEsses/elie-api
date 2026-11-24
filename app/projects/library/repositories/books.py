import logging
from uuid import UUID

from sqlalchemy import select

from app.projects.library.db.db_models import Book, Library
from app.projects.library.models.models import (
    BookData,
    BookResponse,
    ReadingProgressUpdate,
)
from app.shared.database import get_session

logger = logging.getLogger(__name__)


def get_all(user_id: UUID) -> list[BookResponse]:
    with get_session() as session:
        query = (
            select(Book, Library)
            .join(Library, Book.id == Library.book_id)
            .where(Library.user_id == user_id)
        )

        books = session.execute(query).all()

        books_list = [
            BookResponse.model_validate(
                {
                    **book.__dict__,
                    "status": library_entry.status,
                    "pages_read": library_entry.pages_read,
                    "nfc_url": library_entry.nfc_url,
                    "rating": library_entry.rating,
                }
            )
            for book, library_entry in books
        ]

        # sort the books by status and then by title
        status_order = {
            "reading": 0,
            "unread": 1,
            "finished": 2,
        }
        books_list.sort(key=lambda x: (status_order.get(x.status, 3), x.title.lower()))

        return books_list


def get_by_id(user_id: UUID, book_id: int) -> BookResponse | None:
    with get_session() as session:
        query = (
            select(Book, Library)
            .join(Library, Book.id == Library.book_id)
            .where(Library.user_id == user_id, Book.id == book_id)
        )

        result = session.execute(query).first()

        if result is None:
            return None

        book, library_entry = result

        return BookResponse.model_validate(
            {
                **book.__dict__,
                "status": library_entry.status,
                "pages_read": library_entry.pages_read,
                "nfc_url": library_entry.nfc_url,
                "rating": library_entry.rating,
            }
        )


def add(user_id: UUID, book_data: BookData) -> BookResponse | None:
    with get_session() as session:
        # check if the book already exists in the database
        existence_check_query = select(Book).where(Book.isbn == book_data.isbn)
        book = session.scalar(existence_check_query)

        # if the book does not exist in the database, create a new entry for it
        if book is None:
            book = Book(
                **book_data.model_dump()
            )  # converts Pydantic model to dict with right fields for SQLAlchemy model
            session.add(book)
            session.flush()  # we use flush to get back book.id without committing the transaction yet

        # if the book already exists in the database, check if it is already in the user's library
        else:
            existing_entry = session.get(Library, (user_id, book.id))

            if existing_entry is not None:
                raise ValueError("This book is already in your library")

        # if the book is not in the user's library, add it
        nfc_url = f"https://library.app.elie-esses.com/library/{book.id}"
        library_entry = Library(user_id=user_id, book_id=book.id, nfc_url=nfc_url)

        session.add(library_entry)
        book_id = book.id
        session.commit()

        logger.info("Book added to library: %s (ID: %s)", book.title, book.id)

    return get_by_id(user_id, book_id)


def delete(user_id: UUID, book_id: int) -> bool | None:
    with get_session() as session:
        entry = session.get(Library, (user_id, book_id))

        if entry is None:
            return None

        session.delete(entry)
        session.commit()

        logger.info("Book removed from library: ID %s", book_id)

    return True


def update_details(
    user_id: UUID, book_id: int, book_data: BookData
) -> BookResponse | None:
    with get_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return None

        changes = book_data.model_dump(exclude_unset=True)

        for key, value in changes.items():
            setattr(book, key, value)

        session.commit()

        logger.info(
            "Book details updated: ID %s, changes: %s",
            book_id,
            changes,
        )

    return get_by_id(user_id, book_id)


def update_progress(
    user_id: UUID, book_id: int, update: ReadingProgressUpdate
) -> BookResponse | None:
    with get_session() as session:
        entry = session.get(Library, (user_id, book_id))

        if entry is None:
            return None

        changes = update.model_dump(exclude_unset=True)

        book = session.get(Book, book_id)

        # updates pages_read
        if "pages_read" in changes:
            entry.pages_read = changes["pages_read"]

            if book is not None and book.num_pages is not None:
                if entry.pages_read >= book.num_pages:
                    entry.status = "finished"
                elif entry.pages_read <= 0:
                    entry.status = "unread"
                else:
                    entry.status = "reading"

        # updates status and pages_read based on status
        if "status" in changes:
            entry.status = changes["status"]
            if changes["status"] == "unread":
                entry.pages_read = 0
                entry.rating = 0
            elif changes["status"] == "finished":
                # get the total number of pages from the Book table
                if book is not None and book.num_pages is not None:
                    entry.pages_read = book.num_pages

        if "rating" in changes:
            entry.rating = changes["rating"]

        session.commit()

        logger.info(
            "Reading progress updated: book_id=%s, pages=%s, status=%s, rating=%s",
            book_id,
            entry.pages_read,
            entry.status,
            entry.rating,
        )

        return get_by_id(user_id, book_id)

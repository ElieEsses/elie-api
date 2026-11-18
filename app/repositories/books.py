from uuid import UUID

from sqlalchemy import select

from app.db.database import get_session
from app.db.db_models import Book, Library
from app.models.models import (
    BookData,
    BookDetailResponse,
    BookResponse,
    ReadingProgressUpdate,
)


def get_all(user_id: UUID):
    with get_session() as session:
        query = (
            select(Book)
            .join(Library, Book.id == Library.book_id)
            .where(Library.user_id == user_id)
        )
        return session.scalars(query).all()

def get_by_id(user_id: UUID, book_id: int):
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

        return BookDetailResponse(
            **BookResponse.model_validate(book).model_dump(),
            status=library_entry.status,
            pages_read=library_entry.pages_read,
            nfc_url=library_entry.nfc_url,
        )
    
def add(user_id: UUID, book_data: BookData):
    with get_session() as session:
        # check if the book already exists in the database
        existence_check_query = select(Book).where(Book.isbn == book_data.isbn)
        book = session.scalar(existence_check_query)

        # if the book does not exist in the database, create a new entry for it
        if book is None:
            book = Book(**book_data.model_dump()) # converts Pydantic model to dict with right fields for SQLAlchemy model
            session.add(book)
            session.flush() # we use flush to get back book.id without committing the transaction yet

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

    return get_by_id(user_id, book_id)

def delete(user_id: UUID, book_id: int):
    with get_session() as session:
        entry = session.get(Library, (user_id, book_id))

        if entry is None:
            return None

        session.delete(entry)
        session.commit()

    return True

def update_details(user_id: UUID, book_id: int, book_data: BookData):
    with get_session() as session:
        book = session.get(Book, book_id)

        if book is None:
            return None

        changes = book_data.model_dump(exclude_unset=True)

        for key, value in changes.items():
            setattr(book, key, value)

        session.commit()

    print(user_id, book_id)
    result = get_by_id(user_id, book_id)
    print(result)
    return result

def update_progress(user_id: UUID, book_id: int, update: ReadingProgressUpdate):
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
                if entry.pages_read >=book.num_pages:
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
            elif changes["status"] == "finished":
                # get the total number of pages from the Book table
                if book is not None and book.num_pages is not None:
                    entry.pages_read = book.num_pages

        session.commit()

        return get_by_id(user_id, book_id)
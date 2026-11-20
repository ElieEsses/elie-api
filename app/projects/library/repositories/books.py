from uuid import UUID

from sqlalchemy import select

from app.projects.library.db.db_models import Book, Library, Note
from app.projects.library.models.models import (
    BookData,
    BookResponse,
    NoteCreate,
    NoteResponse,
    ReadingProgressUpdate,
)
from app.shared.database import get_session


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

    return get_by_id(user_id, book_id)


def delete(user_id: UUID, book_id: int) -> bool | None:
    with get_session() as session:
        entry = session.get(Library, (user_id, book_id))

        if entry is None:
            return None

        session.delete(entry)
        session.commit()

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
            elif changes["status"] == "finished":
                # get the total number of pages from the Book table
                if book is not None and book.num_pages is not None:
                    entry.pages_read = book.num_pages

        session.commit()

        return get_by_id(user_id, book_id)


def get_notes(user_id: UUID, book_id: int) -> list[NoteResponse]:
    with get_session() as session:
        query = select(Note).where(Note.user_id == user_id, Note.book_id == book_id)

        notes = session.scalars(query).all()

        return [NoteResponse.model_validate(note) for note in notes]


def add_note(user_id: UUID, book_id: int, note_data: NoteCreate) -> NoteResponse:
    with get_session() as session:
        note = Note(user_id=user_id, book_id=book_id, content=note_data.content)
        session.add(note)
        session.commit()
        session.refresh(note)

        return NoteResponse.model_validate(note)


def delete_note(user_id: UUID, book_id: int, note_id: int) -> bool | None:
    with get_session() as session:
        note = session.get(Note, note_id)

        if note is None or note.user_id != user_id or note.book_id != book_id:
            return None

        session.delete(note)
        session.commit()

    return True


def update_note(
    user_id: UUID, book_id: int, note_id: int, note_data: NoteCreate
) -> NoteResponse | None:
    with get_session() as session:
        note = session.get(Note, note_id)

        print(note)

        if note is None or note.user_id != user_id or note.book_id != book_id:
            return None

        note.content = note_data.content
        session.commit()
        session.refresh(note)

    return NoteResponse.model_validate(note)

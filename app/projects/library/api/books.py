from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

import app.projects.library.repositories.books as books
from app.projects.library.models.models import (
    BookData,
    BookDetailResponse,
    BookResponse,
    NoteCreate,
    NoteResponse,
    ReadingProgressUpdate,
)
from app.projects.library.services.book_lookup import get_book_data
from app.shared.auth import get_current_user_id

router = APIRouter(prefix="/books", tags=["Digital Library"])


@router.get("", response_model=list[BookResponse])
def get_books(user_id: UUID = Depends(get_current_user_id)):
    """
    Get all books for the current user.
    """
    return books.get_all(user_id)


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: int, user_id: UUID = Depends(get_current_user_id)):
    """
    Get a specific book by its ID for the current user.
    """
    book = books.get_by_id(user_id, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get(
    "/lookup/{isbn}",
    response_model=BookData | None,
    dependencies=[Depends(get_current_user_id)],
)
def book_lookup(isbn: str):
    """
    Look up a book by its ISBN using the Google Books API and Open Library API.
    """
    return get_book_data(isbn)


@router.post("", response_model=BookDetailResponse)
def add_book(book_data: BookData, user_id: UUID = Depends(get_current_user_id)):
    """
    Add a book to the current user's library.
    """
    try:
        return books.add(user_id, book_data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.patch("/{book_id}", response_model=BookDetailResponse)
def update_book_details(
    book_id: int,
    book_data: BookData,
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Update the details of a specific book in the current user's library.
    """
    result = books.update_details(user_id, book_id, book_data)

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return result


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, user_id: UUID = Depends(get_current_user_id)):
    """
    Delete a specific book from the current user's library.
    """
    success = books.delete(user_id, book_id)

    if not success:
        raise HTTPException(status_code=404, detail="Book not found")

    return None


@router.patch("/{book_id}/progress", response_model=BookDetailResponse)
def update_reading_progress(
    book_id: int,
    update: ReadingProgressUpdate,
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Update the reading progress of a specific book in the current user's library.
    """
    result = books.update_progress(user_id, book_id, update)

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return result


@router.get("/{book_id}/notes", response_model=list[NoteResponse])
def get_notes(book_id: int, user_id: UUID = Depends(get_current_user_id)):
    """
    Get all notes for a specific book in the current user's library.
    """
    result = books.get_notes(user_id, book_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return result


@router.post("/{book_id}/notes", response_model=NoteResponse)
def add_note(
    book_id: int, note_data: NoteCreate, user_id: UUID = Depends(get_current_user_id)
):
    """
    Add a note to a specific book in the current user's library.
    """
    result = books.add_note(user_id, book_id, note_data)

    if result is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return result


@router.patch("/{book_id}/notes/{note_id}", response_model=NoteResponse)
def update_note(
    book_id: int,
    note_id: int,
    note_data: NoteCreate,
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Update a note for a specific book in the current user's library.
    """
    result = books.update_note(user_id, book_id, note_id, note_data)

    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return result


@router.delete("/{book_id}/notes/{note_id}", status_code=204)
def delete_note(
    book_id: int, note_id: int, user_id: UUID = Depends(get_current_user_id)
):
    """
    Delete a note for a specific book in the current user's library.
    """
    success = books.delete_note(user_id, book_id, note_id)

    if not success:
        raise HTTPException(status_code=404, detail="Note not found")

    return None

import logging
from uuid import UUID

from sqlalchemy import select

from app.projects.library.db.db_models import Note
from app.projects.library.models.models import (
    NoteCreate,
    NoteResponse,
)
from app.shared.database import get_session

logger = logging.getLogger(__name__)


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

        logger.info(
            "Note added: user_id=%s, book_id=%s, note_id=%s",
            user_id,
            book_id,
            note.id,
        )

        return NoteResponse.model_validate(note)


def delete_note(user_id: UUID, book_id: int, note_id: int) -> bool | None:
    with get_session() as session:
        note = session.get(Note, note_id)

        if note is None or note.user_id != user_id or note.book_id != book_id:
            return None

        session.delete(note)
        session.commit()

        logger.info(
            "Note deleted: user_id=%s, book_id=%s, note_id=%s",
            user_id,
            book_id,
            note_id,
        )

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

        logger.info(
            "Note updated: user_id=%s, book_id=%s, note_id=%s",
            user_id,
            book_id,
            note.id,
        )

    return NoteResponse.model_validate(note)

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title}, authors={self.authors})"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    isbn: Mapped[str] = mapped_column(unique=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    authors: Mapped[list[str]] = mapped_column(ARRAY(Text))
    first_publish_year: Mapped[int | None] = mapped_column(nullable=True)
    num_pages: Mapped[int | None] = mapped_column(nullable=True)
    cover_url: Mapped[str | None] = mapped_column(nullable=True)


class Library(Base):
    __tablename__ = "libraries"

    def __repr__(self) -> str:
        return f"Library(user_id={self.user_id}, book_id={self.book_id})"

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("books.id"), primary_key=True
    )
    status: Mapped[str] = mapped_column(nullable=False, default="unread")
    pages_read: Mapped[int] = mapped_column(nullable=False, default=0)
    nfc_url: Mapped[str] = mapped_column(
        nullable=False, default="https://library.app.elie-esses.com/library"
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "book_id"],
            ["libraries.user_id", "libraries.book_id"],
            ondelete="CASCADE",
        ),
    )

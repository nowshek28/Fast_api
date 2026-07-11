from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from uuid import uuid4
from datetime import datetime, timezone

from .base import Base

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TodoModel(Base):
    __tablename__ = "todos"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )

    title: Mapped[str]

    description: Mapped[str | None]

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    priority: Mapped[str | None] = mapped_column(
        String,
        default="medium"
    )

    category: Mapped[str | None] = mapped_column(
        String,
        default="other"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow,
        onupdate=_utcnow
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="todos"
    )

    transcript: Mapped["TranscriptModel | None"] = relationship(
        "TranscriptModel",
        back_populates="todo",
        uselist=False,
        cascade="all, delete-orphan"
    )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )

    cognito_sub: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow,
        onupdate=_utcnow
    )

    todos: Mapped[list["TodoModel"]] = relationship(
        "TodoModel",
        back_populates="user"
    )

    transcripts: Mapped[list["TranscriptModel"]] = relationship(
        "TranscriptModel",
        back_populates="user"
    )


class TranscriptModel(Base):
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )

    todo_id: Mapped[str] = mapped_column(
        ForeignKey("todos.id"),
        nullable=False,
        unique=True
    )

    s3_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    original_filename: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="transcripts"
    )

    todo: Mapped["TodoModel"] = relationship(
        "TodoModel",
        back_populates="transcript"
    )


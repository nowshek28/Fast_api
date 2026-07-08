from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import String
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

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
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
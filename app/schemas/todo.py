from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """
    Base schema containing fields shared across multiple Todo schemas.
    """

    title: str = Field(
        ...,            #Mandatory field
        min_length=3,
        max_length=100,
        description="Title of the todo item"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description of the todo item"
    )


class TodoCreate(TodoBase):
    """
    Schema used when creating a new Todo.
    """
    pass


class TodoUpdate(BaseModel):
    """
    Schema used when updating an existing Todo.
    All fields are optional to allow partial updates.
    """

    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500
    )

    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    """
    Schema returned to the client.
    """

    id: UUID
    completed: bool
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TodoListResponse(BaseModel):
    """
    Schema returned when listing multiple todos.
    """

    total: int
    items: List[TodoResponse]
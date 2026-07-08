from datetime import datetime
import enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

class ToDoPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ToDoCategory(str, enum.Enum):
    WORK = "work"
    PERSONAL = "personal"
    OTHER = "other"

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

    priority: ToDoPriority = Field(
        default=ToDoPriority.MEDIUM,
        description="Priority of the todo item"
    )

    category: ToDoCategory = Field(
        default=ToDoCategory.OTHER,
        description="Category of the todo item"
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

    priority: Optional[ToDoPriority] = None

    category: Optional[ToDoCategory] = None


class TodoResponse(TodoBase):
    """
    Schema returned to the client.
    """

    id: UUID
    completed: bool
    user_id: Optional[str] = None
    priority: Optional[ToDoPriority] = None
    category: Optional[ToDoCategory] = None
    created_at: datetime
    updated_at: datetime


class TodoListResponse(BaseModel):
    """
    Schema returned when listing multiple todos.
    """

    total: int
    items: List[TodoResponse]
from datetime import datetime, timezone
from uuid import UUID, uuid4
import logging

from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.exceptions.todo import TodoNotFoundError

logger = logging.getLogger(__name__)

class TodoService:
    """
    Service responsible for Todo business logic.
    """
    def __init__(self, repository):
        self.repository = repository

    def create(self, todo: TodoCreate, user_id: str) -> TodoResponse:
        """
        Create a new Todo.
        """
        logger.info(f"Creating a new todo for user {user_id}.")
        now = datetime.now(timezone.utc)

        new_todo = TodoResponse(
            id=uuid4(),
            title=todo.title,
            description=todo.description,
            completed=False,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )

        logger.info(f"Todo created successfully: {new_todo.id}")
        return self.repository.create(new_todo)
    
    def get_all(self, user_id: str) -> list[TodoResponse]:
        """
        Retrieve all Todos for the given user.
        """
        todos = self.repository.get_all(user_id=user_id)
        logger.info(f"Retrieved {len(todos)} todos for user {user_id}.")
        return todos
    
    def get_by_id(self, todo_id: UUID, user_id: str) -> TodoResponse:
        """
        Retrieve a Todo by its ID, scoped to the given user.
        """
        todo = self.repository.get_by_id(todo_id, user_id=user_id)

        if todo is None:
            logger.warning(f"Todo {todo_id} not found for user {user_id}")
            raise TodoNotFoundError(todo_id)
        logger.info(f"Todo {todo_id} retrieved successfully.")
        return todo
    
    def update(self, todo_id: UUID, todo_update: TodoUpdate, user_id: str) -> TodoResponse:
        """
        Update an existing Todo, scoped to the given user.
        """
        existing_todo = self.repository.get_by_id(todo_id, user_id=user_id)

        if existing_todo is None:
            logger.warning(f"Todo {todo_id} not found for user {user_id}")
            raise TodoNotFoundError(todo_id)

        updated_todo = existing_todo.model_copy(
            update=todo_update.model_dump(exclude_unset=True)
            )
        updated_todo.updated_at = datetime.now(timezone.utc)
        logger.info(f"Todo {todo_id} updated successfully.")
        return self.repository.update(todo_id, updated_todo, user_id=user_id)
    
    def delete(self, todo_id: UUID, user_id: str) -> bool:
        """
        Delete a Todo by its ID, scoped to the given user.
        """
        existing_todo = self.repository.get_by_id(todo_id, user_id=user_id)

        if existing_todo is None:
            logger.warning(f"Todo {todo_id} not found for user {user_id}")
            raise TodoNotFoundError(todo_id)
        logger.info(f"Todo {todo_id} deleted successfully.")

        return self.repository.delete(todo_id, user_id=user_id)



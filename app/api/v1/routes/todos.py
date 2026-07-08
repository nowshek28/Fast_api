from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from uuid import UUID

from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate, ToDoPriority, ToDoCategory
from app.schemas.user import CurrentUserResponse
from app.services.todo_service import TodoService
from app.core.dependencies import get_service
from app.auth.dependencies import get_current_db_user

router = APIRouter()

@router.get(
        "/todos",
        response_model=list[TodoResponse],
        status_code=200,
        )
def get_todos(
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get all Todos of the current user.
    """
    return service.get_all(user_id=current_user.id)

@router.post(
        "/todos",
        response_model=TodoResponse,
        status_code=201,
        )
def create_todo(
    todo: TodoCreate,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Create a new Todo.
    Priority can be one of: "high", "medium", "low".
    Category can be one of: "work", "personal", "other".
    """
    return service.create(todo, user_id=current_user.id)

@router.get(
        "/todos/{todo_id}",
        response_model=TodoResponse,
        status_code=200,
        )
def get_todo_by_id(
    todo_id: UUID,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get a Todo by its ID.
    """
    return service.get_by_id(todo_id, user_id=current_user.id)

@router.get(
        "/todos/completed/{completed}",
        response_model=list[TodoResponse],
        status_code=200,
        )
def get_todos_by_completed(
    completed: bool,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get all Todos of the current user with a specific completed status.
    """
    return service.get_by_completed(completed, user_id=current_user.id)

@router.get(
        "/todos/priority/{priority}",
        response_model=list[TodoResponse],
        status_code=200,
        )
def get_todos_by_priority(
    priority: ToDoPriority,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get all Todos of the current user with a specific priority(high, medium, low).
    """
    return service.get_by_priority(priority, user_id=current_user.id)

@router.get(
        "/todos/category/{category}",
        response_model=list[TodoResponse],
        status_code=200,
        )
def get_todos_by_category(
    category: ToDoCategory,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Get all Todos of the current user with a specific category(work, personal, other).
    """
    return service.get_by_category(category, user_id=current_user.id)

@router.put(
        "/todos/{todo_id}",
        response_model=TodoResponse,
        status_code=200,
        )
def update_todo(
    todo_id: UUID,
    todo_update: TodoUpdate,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Update an existing Todo.
    Priority can be one of: "high", "medium", "low".
    Category can be one of: "work", "personal", "other".
    """
    return service.update(todo_id, todo_update, user_id=current_user.id)

@router.delete(
        "/todos/{todo_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        )
def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_service),
    current_user: CurrentUserResponse = Depends(get_current_db_user),
):
    """
    Delete a Todo by its ID.
    """
    service.delete(todo_id, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

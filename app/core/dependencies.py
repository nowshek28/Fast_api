from fastapi import Depends

from app.repositories.postgres_todo_repository import PostgresTodoRepository
from app.repositories.postgres_user_repository import PostgresUserRepository
from app.services.todo_service import TodoService
from app.database.database import get_db
from app.services.user_service import UserService


def get_postgres_repository(
    db=Depends(get_db),
):
    return PostgresTodoRepository(db)


def get_service(
    repository=Depends(get_postgres_repository),
):
    return TodoService(repository)

def get_user_repository(
    db=Depends(get_db),
):
    return PostgresUserRepository(db)

def get_user_service(
    repository=Depends(get_user_repository),
):
    return UserService(repository)


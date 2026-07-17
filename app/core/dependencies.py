from fastapi import Depends

from app.repositories.postgres_todo_repository import PostgresTodoRepository
from app.repositories.postgres_user_repository import PostgresUserRepository
from app.repositories.transcript_repository import TranscriptRepository

from app.services.todo_service import TodoService
from app.services.transcript_service import TranscriptService
from app.services.user_service import UserService
from app.services.storage_service import StorageService
from app.services.etl.etl_service import ETLService

from app.database.database import get_db
from app.database.chroma import transcript_collection, chroma_client


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

def get_transcript_repository(
    db=Depends(get_db),
):
    return TranscriptRepository(db)

def get_s3_storage_service():
    return StorageService()

def get_etl_service():
    return ETLService()

def get_transcript_service(
    transcript_repository=Depends(get_transcript_repository),
    todo_repository=Depends(get_postgres_repository),
    storage_service=Depends(get_s3_storage_service),
    etl_service=Depends(get_etl_service),
):
    return TranscriptService(transcript_repository, todo_repository, storage_service, etl_service)

def get_chroma_client():
    return chroma_client

def get_transcript_collection():
    return transcript_collection

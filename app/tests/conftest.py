import pytest

from datetime import datetime, timezone
from sqlalchemy import create_engine, delete as sql_delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.storage.json_storage import JsonStorage
from app.repositories.json_todo_repository import JsonTodoRepository
from app.services.todo_service import TodoService
from app.tests.fakes import FakeStorageService, FakeTodoRepository

from fastapi.testclient import TestClient
from app.main import app
from app.database.base import Base
from app.database.models import TodoModel
from app.core.dependencies import get_db, get_s3_storage_service
from app.auth.dependencies import get_current_db_user
from app.schemas.user import CurrentUserResponse


# ---------------------------------------------------------------------------
# Shared in-memory SQLite engine.
# StaticPool forces all connections to reuse the same in-memory database so
# that the tables created here are visible inside the TestClient requests.
# The production PostgreSQL database is never touched by any test.
# ---------------------------------------------------------------------------
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=_test_engine)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# A stable fake user injected into every API test request.
FAKE_USER_ID = "00000000-0000-0000-0000-000000000001"
_fake_user = CurrentUserResponse(
    id=FAKE_USER_ID,
    cognito_sub="fake-user-sub-uuid",
    username="Test User",
    created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
)


@pytest.fixture
def storage(tmp_path):
    """Creates a temporary JSON storage for each test."""
    file_path = tmp_path / "test_todos.json"
    storage = JsonStorage(str(file_path))
    yield storage


@pytest.fixture
def repository(storage):
    """Creates a JsonTodoRepository instance using the temporary storage."""
    return JsonTodoRepository(storage)


@pytest.fixture
def service():
    """Creates a TodoService backed by an in-memory FakeTodoRepository."""
    return TodoService(FakeTodoRepository())


@pytest.fixture(scope="function")
def client():
    """
    TestClient wired to an in-memory SQLite database with auth bypassed.

    - The production PostgreSQL database is never read or written.
    - get_current_db_user is overridden to return a stable fake user so that
      every authenticated todo endpoint works without real JWTs or Cognito.
    - Each test starts with a clean table (all rows are deleted on teardown).
    """
    session = _TestingSessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_db_user] = lambda: _fake_user
    app.dependency_overrides[get_s3_storage_service] = lambda: FakeStorageService()  # Mock S3 storage service

    yield TestClient(app)

    # Teardown: clear all rows so the next test starts with an empty database.
    session.rollback()
    session.execute(sql_delete(TodoModel))
    session.commit()
    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)

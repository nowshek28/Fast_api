from datetime import datetime,timezone
from uuid import uuid4

from app.schemas.todo import TodoResponse

def test_create_todo(repository):

    todo = TodoResponse(
        id=uuid4(),
        title="Learn FastAPI",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    created = repository.create(todo)

    assert created.id == todo.id
    assert created.title == "Learn FastAPI"
    assert created.description == "Testing repository"
    assert created.completed is False
    assert created.priority == "medium"
    assert created.category == "other"


def test_get_all_todos(repository):
    todo1 = TodoResponse(
        id=uuid4(),
        title="Learn FastAPI",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    todo2 = TodoResponse(
        id=uuid4(),
        title="Learn Pytest",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo1)
    repository.create(todo2)

    todos = repository.get_all()

    assert len(todos) == 2
    assert todos[0].id == todo1.id
    assert todos[1].id == todo2.id


def test_get_todo_by_id(repository):
    todo = TodoResponse(
        id=uuid4(),
        title="Find Todo by ID",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo)

    fetched_todo = repository.get_by_id(todo.id)

    assert fetched_todo is not None
    assert fetched_todo.id == todo.id
    assert fetched_todo.title == "Find Todo by ID"

def test_get_todo_by_completed(repository):
    todo1 = TodoResponse(
        id=uuid4(),
        title="Completed Todo",
        description="Testing repository",
        completed=True,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    todo2 = TodoResponse(
        id=uuid4(),
        title="Incomplete Todo",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo1)
    repository.create(todo2)

    completed_todos = repository.get_by_completed(True)
    incomplete_todos = repository.get_by_completed(False)

    assert len(completed_todos) == 1
    assert completed_todos[0].id == todo1.id

    assert len(incomplete_todos) == 1
    assert incomplete_todos[0].id == todo2.id

def test_get_todo_by_priority(repository):
    todo1 = TodoResponse(
        id=uuid4(),
        title="High Priority Todo",
        description="Testing repository",
        completed=False,
        priority="high",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    todo2 = TodoResponse(
        id=uuid4(),
        title="Low Priority Todo",
        description="Testing repository",
        completed=False,
        priority="low",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo1)
    repository.create(todo2)

    high_priority_todos = repository.get_by_priority("high")
    low_priority_todos = repository.get_by_priority("low")

    assert len(high_priority_todos) == 1
    assert high_priority_todos[0].id == todo1.id

    assert len(low_priority_todos) == 1
    assert low_priority_todos[0].id == todo2.id

def test_get_todo_by_category(repository):
    todo1 = TodoResponse(
        id=uuid4(),
        title="Work Todo",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="work",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    todo2 = TodoResponse(
        id=uuid4(),
        title="Personal Todo",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="personal",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo1)
    repository.create(todo2)

    work_todos = repository.get_by_category("work")
    personal_todos = repository.get_by_category("personal")

    assert len(work_todos) == 1
    assert work_todos[0].id == todo1.id

    assert len(personal_todos) == 1
    assert personal_todos[0].id == todo2.id

def test_update_todo(repository):
    todo = TodoResponse(
        id=uuid4(),
        title="Update Todo",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo)

    updated_todo = TodoResponse(
        id=todo.id,
        title="Updated Todo",
        description="Updated description",
        completed=True,
        priority="high",
        category="work",
        created_at=todo.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    result = repository.update(todo.id, updated_todo)

    assert result is not None
    assert result.title == "Updated Todo"
    assert result.description == "Updated description"
    assert result.completed is True
    assert result.priority == "high"
    assert result.category == "work"

def test_delete_todo(repository):
    todo = TodoResponse(
        id=uuid4(),
        title="Delete Todo",
        description="Testing repository",
        completed=False,
        priority="medium",
        category="other",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repository.create(todo)

    deleted = repository.delete(todo.id)

    assert deleted is True
    assert repository.get_by_id(todo.id) is None

    
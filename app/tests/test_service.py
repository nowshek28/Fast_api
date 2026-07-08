from app.schemas.todo import TodoCreate

FAKE_USER_ID = "test-user-id"


def test_create_generates_uuid(service):
    """
    Test the creation of a new todo item.
    """
    todo = TodoCreate(
        title="Learn FastAPI",
        description="Service test",
        priority="medium",
        category="other"
    )

    created = service.create(todo, user_id=FAKE_USER_ID)

    assert created.id is not None

def test_create_sets_completed_false(service):
    """
    Test that a new todo item is created with completed set to False.
    """
    todo = TodoCreate(
        title="Learn FastAPI",
        description="Service test",
        priority="medium",
        category="other"
    )

    created = service.create(todo, user_id=FAKE_USER_ID)

    assert created.completed is False

def test_create_generates_timestamps(service):
    """
    Test that a new todo item is created with created_at and updated_at timestamps.
    """
    todo = TodoCreate(
        title="Learn FastAPI",
        description="Service test",
        priority="medium",
        category="other"
    )

    created = service.create(todo, user_id=FAKE_USER_ID)

    assert created.created_at is not None
    assert created.updated_at is not None


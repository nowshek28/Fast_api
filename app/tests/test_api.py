def test_health(client):
    """
    Test the health check endpoint.
    """
    response = client.get("api/v1/health")
    assert response.status_code == 200

#####################################################################################  

def test_root(client):
    """
    Test the root endpoint.
    """
    from app.core.config import settings

    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert data["status"] == "running"
    assert data["docs"] == "/docs"

#####################################################################################  

def test_create_todo_success(client):
    """
    Test the creation of a new todo item.
    """
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo item.",
        "completed": False,
        "priority": "medium",
        "category": "other"
    }
    response = client.post("/api/v1/todos", json=todo_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert data["completed"] == todo_data["completed"]
    assert data["id"] is not None
    assert data["priority"] is not None
    assert data["category"] is not None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

def test_title_too_short(client):
    """
    Test creating a todo item with a title that is too short.
    """
    todo_data = {
        "title": "Hi",  # Title is too short (less than 3 characters)
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    response = client.post("/api/v1/todos", json=todo_data)

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "title"]
    assert data["detail"][0]["msg"] == "String should have at least 3 characters"

def test_title_too_long(client):
    """
    Test creating a todo item with a title that is too long.
    """
    todo_data = {
        "title": "T" * 101,  # Title is too long (more than 100 characters)
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    response = client.post("/api/v1/todos", json=todo_data)

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "title"]
    assert data["detail"][0]["msg"] == "String should have at most 100 characters"

def test_missing_title(client):
    """
    Test creating a todo item with a missing title.
    """
    todo_data = {
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    response = client.post("/api/v1/todos", json=todo_data)

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "title"]
    assert data["detail"][0]["msg"] == "Field required"

def test_description_too_long(client):
    """
    Test creating a todo item with a description that is too long.
    """
    todo_data = {
        "title": "Test Todo",
        "description": "D" * 501,  # Description is too long (more than 500 characters)
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    response = client.post("/api/v1/todos", json=todo_data)

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "description"]
    assert data["detail"][0]["msg"] == "String should have at most 500 characters"


#####################################################################################  

def test_get_todo(client):
    """
    Test retrieving a todo item by ID.
    """
    # First, create a new todo item
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    create_response = client.post("/api/v1/todos", json=todo_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, retrieve the created todo item
    get_response = client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 200
    retrieved_todo = get_response.json()
    assert retrieved_todo == created_todo

#####################################################################################  

def test_get_todo_by_id(client):
    """
    Test retrieving a todo item by its ID.
    """
    # First, create a new todo item
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    create_response = client.post("/api/v1/todos", json=todo_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, retrieve the created todo item by its ID
    get_response = client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 200
    retrieved_todo = get_response.json()
    assert retrieved_todo == created_todo

def test_get_todo_invalid_uuid(client):
    """
    Test retrieving a todo item with an invalid ID format.
    """
    invalid_id = "invalid-id"
    response = client.get(f"/api/v1/todos/{invalid_id}")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["path", "todo_id"]
    assert "Input should be a valid UUID" in data["detail"][0]["msg"]

def test_get_todo_not_found(client):
    """
    Test retrieving a todo item that does not exist.
    """
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/todos/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Todo with id '{non_existent_id}' was not found."

##################################################################################### 

def test_get_todos_by_completed(client):
    """
    Test retrieving todos by their completed status.
    """
    # Create two todo items: one completed and one not completed
    todo_data_1 = {
        "title": "Completed Todo",
        "description": "This todo is completed.",
        "priority": "medium",
        "category": "other",
        "completed": True
    }
    todo_data_2 = {
        "title": "Not Completed Todo",
        "description": "This todo is not completed.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    client.post("/api/v1/todos", json=todo_data_1)
    client.post("/api/v1/todos", json=todo_data_2)

    # Retrieve todos that are completed
    response_completed = client.get("/api/v1/todos/completed/true")
    assert response_completed.status_code == 200
    todos_completed = response_completed.json()
    assert all(todo["completed"] is True for todo in todos_completed)

    # Retrieve todos that are not completed
    response_not_completed = client.get("/api/v1/todos/completed/false")
    assert response_not_completed.status_code == 200
    todos_not_completed = response_not_completed.json()
    assert all(todo["completed"] is False for todo in todos_not_completed)

##################################################################################### 

def test_get_todos_by_priority(client):
    """
    Test retrieving todos by their priority.
    """
    # Create three todo items with different priorities
    todo_data_high = {
        "title": "High Priority Todo",
        "description": "This todo has high priority.",
        "priority": "high",
        "category": "other",
        "completed": False
    }
    todo_data_medium = {
        "title": "Medium Priority Todo",
        "description": "This todo has medium priority.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    todo_data_low = {
        "title": "Low Priority Todo",
        "description": "This todo has low priority.",
        "priority": "low",
        "category": "other",
        "completed": False
    }
    client.post("/api/v1/todos", json=todo_data_high)
    client.post("/api/v1/todos", json=todo_data_medium)
    client.post("/api/v1/todos", json=todo_data_low)

    # Retrieve todos with high priority
    response_high = client.get("/api/v1/todos/priority/high")
    assert response_high.status_code == 200
    todos_high = response_high.json()
    assert all(todo["priority"] == "high" for todo in todos_high)

    # Retrieve todos with medium priority
    response_medium = client.get("/api/v1/todos/priority/medium")
    assert response_medium.status_code == 200
    todos_medium = response_medium.json()
    assert all(todo["priority"] == "medium" for todo in todos_medium)

    # Retrieve todos with low priority
    response_low = client.get("/api/v1/todos/priority/low")
    assert response_low.status_code == 200
    todos_low = response_low.json()
    assert all(todo["priority"] == "low" for todo in todos_low)

def test_get_todos_by_invalid_priority(client):
    """
    Test retrieving todos with an invalid priority value.
    """
    invalid_priority = "urgent"  # This is not a valid priority
    response = client.get(f"/api/v1/todos/priority/{invalid_priority}")
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()["detail"][0]
    assert data["loc"] == ["path", "priority"]
    assert data["type"] == "enum"  # The error type for invalid enum values
 
##################################################################################### 

def test_get_todos_by_category(client):
    """
    Test retrieving todos by their category.
    """
    # Create three todo items with different categories
    todo_data_work = {
        "title": "Work Todo",
        "description": "This todo is for work.",
        "priority": "medium",
        "category": "work",
        "completed": False
    }
    todo_data_personal = {
        "title": "Personal Todo",
        "description": "This todo is personal.",
        "priority": "medium",
        "category": "personal",
        "completed": False
    }
    todo_data_other = {
        "title": "Other Todo",
        "description": "This todo is for other purposes.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    client.post("/api/v1/todos", json=todo_data_work)
    client.post("/api/v1/todos", json=todo_data_personal)
    client.post("/api/v1/todos", json=todo_data_other)

    # Retrieve todos in the 'work' category
    response_work = client.get("/api/v1/todos/category/work")
    assert response_work.status_code == 200
    todos_work = response_work.json()
    assert all(todo["category"] == "work" for todo in todos_work)

    # Retrieve todos in the 'personal' category
    response_personal = client.get("/api/v1/todos/category/personal")
    assert response_personal.status_code == 200
    todos_personal = response_personal.json()
    assert all(todo["category"] == "personal" for todo in todos_personal)

    # Retrieve todos in the 'other' category
    response_other = client.get("/api/v1/todos/category/other")
    assert response_other.status_code == 200
    todos_other = response_other.json()
    assert all(todo["category"] == "other" for todo in todos_other)

def test_get_todos_by_invalid_category(client):
    """
    Test retrieving todos with an invalid category value.
    """
    invalid_category = "hobby"  # This is not a valid category
    response = client.get(f"/api/v1/todos/category/{invalid_category}")
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()["detail"][0]
    assert data["loc"] == ["path", "category"]
    assert data["type"] == "enum"  # The error type for invalid enum values

##################################################################################### 

def test_update_todo_success(client):
    """
    Test updating an existing todo item.
    """
    # First, create a new todo item
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": False
    }
    create_response = client.post("/api/v1/todos", json=todo_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, update the created todo item
    updated_data = {
        "title": "Updated Test Todo",
        "description": "This is an updated test todo item.",
        "priority": "high",
        "category": "work",
        "completed": True
    }
    update_response = client.put(f"/api/v1/todos/{todo_id}", json=updated_data)
    assert update_response.status_code == 200
    updated_todo = update_response.json()
    assert updated_todo["title"] == updated_data["title"]
    assert updated_todo["description"] == updated_data["description"]
    assert updated_todo["completed"] == updated_data["completed"]
    assert updated_todo["id"] == todo_id
    assert updated_todo["created_at"] == created_todo["created_at"]
    assert updated_todo["updated_at"] != created_todo["updated_at"]

def test_update_todo_not_found(client):
    """
    Test updating a todo item that does not exist.
    """
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    updated_data = {
        "title": "Updated Test Todo",
        "description": "This is an updated test todo item.",
        "priority": "medium",
        "category": "other",
        "completed": True
    }
    response = client.put(f"/api/v1/todos/{non_existent_id}", json=updated_data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Todo with id '{non_existent_id}' was not found."


#####################################################################################  

def test_delete_todo_success(client):
    """
    Test deleting an existing todo item.
    """
    # First, create a new todo item
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo item.",
        "completed": False
    }
    create_response = client.post("/api/v1/todos", json=todo_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]

    # Now, delete the created todo item
    delete_response = client.delete(f"/api/v1/todos/{todo_id}")
    assert delete_response.status_code == 204

    # Verify that the todo item no longer exists
    get_response = client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 404

def test_delete_todo_not_found(client):
    """
    Test deleting a todo item that does not exist.
    """
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/v1/todos/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Todo with id '{non_existent_id}' was not found."
    
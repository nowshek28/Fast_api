
from app.schemas.todo import TodoResponse
from uuid import UUID


class JsonTodoRepository:
    """
    Repository responsible for storing and retrieving Todo items.
    Currently uses in-memory storage.
    """
    def __init__(self, storage):
        self.storage = storage

    def _load_todos(self) -> list[TodoResponse]:
        """
        load todo from json storage and convert them to TodoResponse models.
        """

        data = self.storage.load()

        return [
            TodoResponse.model_validate(todo) for todo in data
        ]
    
    def _save_todos(self, todos: list[TodoResponse]) -> None:
        """
        Save the list of TodoResponse models to JSON storage.
        """
        data = [todo.model_dump(mode="json") for todo in todos]
        self.storage.save(data)


    def create(self, todo: TodoResponse) -> TodoResponse:
        """
        Store a new todo in memory.
        """
        todos = self._load_todos()
        todos.append(todo)
        self._save_todos(todos)
        return todo

    def get_all(self) -> list[TodoResponse]:
        """
        Retrieve all Todo items.
        """
        return self._load_todos()
    
    def get_by_id(self, todo_id: UUID) -> TodoResponse | None:
        """
        Retrieve a Todo item by its ID.
        """
        todos = self._load_todos()
        
        for todo in todos:
            if todo.id == todo_id:
                return todo
        return None
    
    def get_by_completed(self, completed: bool) -> list[TodoResponse]:
        """
        Retrieve all Todo items filtered by their completion status.
        """
        todos = self._load_todos()
        return [todo for todo in todos if todo.completed == completed]
    
    def get_by_priority(self, priority: str) -> list[TodoResponse]:
        """
        Retrieve all Todo items filtered by their priority.
        """
        todos = self._load_todos()
        return [todo for todo in todos if todo.priority == priority]
    
    def get_by_category(self, category: str) -> list[TodoResponse]:
        """
        Retrieve all Todo items filtered by their category.
        """
        todos = self._load_todos()
        return [todo for todo in todos if todo.category == category]
    
    def update(self, todo_id: UUID, updated_todo: TodoResponse) -> TodoResponse | None:
        """
        Update an existing Todo item.
        """
        todos = self._load_todos()
        for index, todo in enumerate(todos):
            if todo.id == todo_id:
                todos[index] = updated_todo
                self._save_todos(todos)
                return updated_todo
        return None
    
    def delete(self, todo_id: UUID) -> bool:
        """
        Delete a Todo item by its ID.
        Returns True if the item was deleted, False if not found.
        """
        todos = self._load_todos()
        for index, todo in enumerate(todos):
            if todo.id == todo_id:
                del todos[index]
                self._save_todos(todos)
                return True
        return False
    
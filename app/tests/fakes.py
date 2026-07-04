from app.auth.exceptions import InvalidCredentialsError, UserNotConfirmedError
from app.auth.schemas import ConfirmSignUpResponse
from app.schemas.todo import TodoResponse


class FakeCognitoClient:
    """
    In-memory Cognito stand-in for unit/integration tests.
    No AWS credentials or network access required.
    """

    VALID_CONFIRMATION_CODE = "123456"

    def __init__(self):
        # email -> {password, name, confirmed}
        self._users: dict = {}

    def sign_up(self, email: str, password: str, name: str) -> dict:
        if email in self._users:
            raise InvalidCredentialsError("User already exists.")
        self._users[email] = {"password": password, "name": name, "confirmed": False}
        return {"UserConfirmed": False, "UserSub": "fake-user-sub-uuid"}

    def confirm_sign_up(self, email: str, confirmation_code: str) -> ConfirmSignUpResponse:
        if email not in self._users:
            raise InvalidCredentialsError("User not found.")
        if confirmation_code != self.VALID_CONFIRMATION_CODE:
            raise InvalidCredentialsError("Invalid confirmation code.")
        self._users[email]["confirmed"] = True
        return ConfirmSignUpResponse(message="User confirmed successfully.")

    def login(self, username: str, password: str) -> dict:
        user = self._users.get(username)
        if user is None or user["password"] != password:
            raise InvalidCredentialsError("Invalid username or password.")
        if not user["confirmed"]:
            raise UserNotConfirmedError("User is not confirmed.")
        return {
            "AuthenticationResult": {
                "AccessToken": "fake-access-token",
                "IdToken": "fake-id-token",
                "RefreshToken": "fake-refresh-token",
                "ExpiresIn": 3600,
                "TokenType": "Bearer",
            }
        }


class FakeTodoRepository:

    def __init__(self):
        self.todos = []

    def create(self, todo: TodoResponse):
        self.todos.append(todo)
        return todo

    def get_all(self):
        return self.todos

    def get_by_id(self, todo_id):
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def update(self, todo_id, updated_todo):
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                self.todos[i] = updated_todo
                return updated_todo
        return None

    def delete(self, todo_id):
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                return True
        return False
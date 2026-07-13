from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.auth.exceptions import InvalidCredentialsError, NotAuthorizedError, UserNotConfirmedError
from app.auth.schemas import ConfirmSignUpResponse, RefreshTokenResponse, SignOutResponse
from app.database.models import TodoModel, TranscriptModel
from app.schemas.todo import TodoResponse, TodoCreate


class FakeJWTVerifier:
    """
    In-memory JWT verifier for tests — no crypto, no network.
    Any token equal to VALID_TOKEN is accepted; all others raise ValueError.
    """
    VALID_TOKEN = "fake-access-token"
    FAKE_CLAIMS = {
        "sub": "fake-user-sub-uuid",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_FAKEPOOL",
        "client_id": "fake-client-id",
        "token_use": "access",
        "username": "test@example.com",
        "exp": 9999999999,
        "iat": 1000000000,
        "auth_time": 1000000000,
    }

    def verify_access_token(self, token: str) -> dict:
        if token != self.VALID_TOKEN:
            raise ValueError("Invalid token.")
        return self.FAKE_CLAIMS


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

    def refresh_access_token(self, username: str, refresh_token: str) -> RefreshTokenResponse:
        if username not in self._users or refresh_token != "fake-refresh-token":
            raise NotAuthorizedError("Invalid refresh token.")
        return RefreshTokenResponse(
            access_token="fake-new-access-token",
            id_token="fake-new-id-token",
            expires_in=3600,
            token_type="Bearer",
        )

    def global_sign_out(self, access_token: str) -> SignOutResponse:
        if access_token != "fake-access-token":
            raise NotAuthorizedError("Invalid access token.")
        return SignOutResponse(message="User signed out globally successfully.")

    def get_user_attributes(self, access_token: str) -> dict:
        """Return fake user attributes — no network call needed in tests."""
        if access_token != "fake-access-token":
            raise NotAuthorizedError("Invalid access token.")
        return {"name": "Test User", "email": "test@example.com"}


class FakeTodoRepository:

    def __init__(self):
        self.todos = []

    def create(self,
        *,
        title: str,
        description: str | None,
        user_id: str,
        priority: str,
        category: str,
        ) -> TodoModel:
        now = datetime.now(timezone.utc)
        todo = TodoModel(
            id=str(UUID(int=0)),  # Use a fixed UUID for testing
            title=title,
            description=description,
            completed=False,
            user_id=user_id,
            priority=priority,
            category=category,
            created_at=now,
            updated_at=now,
        )
        self.todos.append(todo)
        return todo

    def get_all(self, user_id: str = None):
        if user_id is not None:
            return [t for t in self.todos if t.user_id == user_id]
        return list(self.todos)

    def get_by_id(self, todo_id, user_id: str = None):
        for todo in self.todos:
            if todo.id == todo_id:
                if user_id is None or todo.user_id == user_id:
                    return todo
        return None
    
    def get_by_completed(self, completed: bool, user_id: str = None):
        if user_id is not None:
            return [t for t in self.todos if t.completed == completed and t.user_id == user_id]
        return [t for t in self.todos if t.completed == completed]
    
    def get_by_title(self, title: str, user_id: str = None):
        if user_id is not None:
            return [t for t in self.todos if t.title == title and t.user_id == user_id]
        return [t for t in self.todos if t.title == title]
    
    def get_by_category(self, category: str, user_id: str = None):
        if user_id is not None:
            return [t for t in self.todos if t.category == category and t.user_id == user_id]
        return [t for t in self.todos if t.category == category]

    def update(self, todo_id, updated_todo, user_id: str = None):
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                if user_id is None or todo.user_id == user_id:
                    self.todos[i] = updated_todo
                    return updated_todo
        return None

    def delete(self, todo_id, user_id: str = None):
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                if user_id is None or todo.user_id == user_id:
                    del self.todos[i]
                    return True
        return False


class FakeTranscriptRepository:

    def __init__(self):
        self.transcripts = []

    def create(
            self,
            *,
            todo_id: str,
            user_id: str,
            s3_key: str,
            original_file_name: str,
            file_type: str,
            file_size: int,
        ) -> TranscriptModel:

        transcript = TranscriptModel(
            todo_id=todo_id,
            user_id=user_id,
            s3_key=s3_key,
            original_filename=original_file_name,
            file_type=file_type,
            file_size=file_size
        )
        self.transcripts.append(transcript)
        return transcript
    
    def get_by_id(
            self,
            transcript_id: str,
            user_id: str
        ) -> TranscriptModel | None:

        for transcript in self.transcripts:
            if transcript.id == transcript_id and transcript.user_id == user_id:
                return transcript
        return None
    
    def get_by_todo_id(
            self,
            todo_id: str,
            user_id: str
        ) -> TranscriptModel | None:

        for transcript in self.transcripts:
            if transcript.todo_id == todo_id and transcript.user_id == user_id:
                return transcript
        return None
    
    def exists_for_todo(
            self,
            todo_id: str,
            user_id: str
        ) -> bool:

        for transcript in self.transcripts:
            if transcript.todo_id == todo_id and transcript.user_id == user_id:
                return True
        return False
    
    def delete(
            self,
            transcript_id: str,
            user_id: str
        ) -> None:

        for i, transcript in enumerate(self.transcripts):
            if transcript.id == transcript_id and transcript.user_id == user_id:
                del self.transcripts[i]
                return
            
    def get_file_name(
            self,
            transcript_id: str,
            user_id: str
        ) -> str | None:

        for transcript in self.transcripts:
            if transcript.id == transcript_id and transcript.user_id == user_id:
                return transcript.original_filename
        return None
    
    def get_by_user_id(self, user_id: str = None):
        if user_id is not None:
            return [t for t in self.transcripts if t.user_id == user_id]
        return self.transcripts
    
    def get_download_key_orignal(self, transcript_id: str, user_id: str):
        for transcript in self.transcripts:
            if transcript.id == transcript_id and transcript.user_id == user_id:
                return transcript.s3_key, transcript.original_filename
        return (None, None)
    

class FakeStorageService:

    async def upload_transcript(self, todo_id, file):
        fake_UUID = uuid4()
        s3_key = f"{fake_UUID}.txt"
        file_size = len(await file.read())
        return s3_key, file_size

    def delete_transcript(self, s3_key):
        return True

    def object_exists(self, s3_key):
        return True
    
    def download_transcript_to_file(self, s3_key, local_path):
        return True
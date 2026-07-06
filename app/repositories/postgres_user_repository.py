from sqlalchemy.orm import Session

from app.database.models import UserModel
from app.schemas.user import UserCreate, CurrentUserResponse

class PostgresUserRepository:
    """
    Repository responsible for storing and retrieving User items in a PostgreSQL database.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_response(self, model: UserModel) -> CurrentUserResponse:
        """Convert a SQLAlchemy UserModel to a Pydantic CurrentUserResponse."""
        return CurrentUserResponse(
            id=model.id,
            cognito_sub=model.cognito_sub,
            username=model.username,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_by_cognito_sub(self, cognito_sub: str) -> CurrentUserResponse | None:
        """Retrieve a User item by its Cognito sub from the database."""
        model = (self.db.query(UserModel)
                .filter(UserModel.cognito_sub == cognito_sub)
                .first()
                )
        if model:
            return self._to_response(model)
        return None

    def create(self, user: UserCreate) -> CurrentUserResponse:
        """Create a new User item in the database."""
        new_user = UserModel(
            cognito_sub=user.cognito_sub,
            username=user.username
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return self._to_response(new_user)
    
    def update(self, user: UserModel) -> CurrentUserResponse:
        """Update an existing User item in the database."""
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)
    
    def delete(self, user: UserModel) -> bool:
        """Delete a User item from the database."""
        self.db.delete(user)
        self.db.commit()
        return True
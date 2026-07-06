

import logging

from app.auth.schemas import TokenClaims
from app.schemas.user import UserCreate, CurrentUserResponse
from app.database.models import UserModel

logger = logging.getLogger(__name__)

class UserService:
    """
    Service responsible for handling business logic related to User items.
    """

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user_by_cognito_sub(self, cognito_sub: str) -> CurrentUserResponse | None:
        """Retrieve a User item by its Cognito sub."""
        logger.debug(f"Looking up user by cognito_sub: {cognito_sub}")
        user = self.user_repository.get_by_cognito_sub(cognito_sub)
        if user is None:
            logger.warning(f"User not found for cognito_sub: {cognito_sub}")
        return user
    
    def get_or_create_user(self, claims: TokenClaims) -> CurrentUserResponse:
        """
        Retrieve a User item by its Cognito sub, or create a new one if it doesn't exist.
        """
        cognito_sub = claims.sub
        logger.debug(f"get_or_create_user called for cognito_sub: {cognito_sub}")
        user = self.get_user_by_cognito_sub(cognito_sub)

        if user is None:
            logger.info(f"No existing user for cognito_sub: {cognito_sub}. Creating new record.")
            user_create = UserCreate(
                cognito_sub=cognito_sub,
                username=claims.username
            )
            user = self.create_user(user_create)

        return user

    def create_user(self, user_create: UserCreate) -> CurrentUserResponse:
        """Create a new User item."""
        logger.info(f"Creating user with cognito_sub: {user_create.cognito_sub}")
        user = self.user_repository.create(user_create)
        logger.info(f"User created successfully: {user.id}")
        return user

    def update_user(self, user_model: UserModel) -> CurrentUserResponse:
        """Update an existing User item."""
        logger.info(f"Updating user: {user_model.id}")
        user = self.user_repository.update(user_model)
        logger.info(f"User updated successfully: {user.id}")
        return user

    def delete_user(self, user_model: UserModel) -> bool:
        """Delete a User item."""
        logger.info(f"Deleting user: {user_model.id}")
        result = self.user_repository.delete(user_model)
        if result:
            logger.info(f"User deleted successfully: {user_model.id}")
        else:
            logger.warning(f"Failed to delete user: {user_model.id}")
        return result
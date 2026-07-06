from datetime import datetime

from pydantic import BaseModel

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    cognito_sub: str

    username: str

class CurrentUserResponse(BaseModel):
    """Schema for returning the current user's data."""
    id: str
    cognito_sub: str
    username: str
    created_at: datetime
    updated_at: datetime
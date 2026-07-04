from pydantic import BaseModel, EmailStr, Field

class SignUpRequest(BaseModel):
    """
    Schema for sign-up request data.
    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password, must be at least 8 characters long.
        name (str): The user's full name.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    
class SignUpResponse(BaseModel):
    """
    Response schema for successful sign-up.
    Attributes:
        message (str): A message indicating the result of the sign-up operation.
        user_confirmed (bool): Indicates whether the user is confirmed.
    """
    message: str
    user_confirmed: bool

class ConfirmSignUpRequest(BaseModel):
    """
    Schema for confirm sign-up request data.
    Attributes:
        email (EmailStr): The user's email address.
        confirmation_code (str): The confirmation code sent to the user's email.
    """
    email: EmailStr
    confirmation_code: str = Field(..., pattern=r'^\d{6}$')  # Assuming confirmation code is 6 digits long

class ConfirmSignUpResponse(BaseModel):
    """
    Response schema for successful confirmation of sign-up.
    Attributes:
        message (str): A message indicating the result of the confirmation operation.
    """
    message: str
    
class LoginRequest(BaseModel):
    """
    Schema for login request data.
    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password, must be at least 8 characters long.
    """

    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    """
    Response schema for successful login.
    """
    access_token:str
    id_token:str
    refresh_token:str
    expires_in:int
    token_type:str


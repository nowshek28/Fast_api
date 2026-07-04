from fastapi import Depends

from app.auth.cognito import CognitoClient
from app.auth.service import AuthService

def get_cognito_client() -> CognitoClient:
    """
    Dependency to get an instance of CognitoClient.
    """
    return CognitoClient()

def get_auth_service(cognito_client: CognitoClient = Depends(get_cognito_client)) -> AuthService:
    """
    Dependency to get an instance of AuthService.
    """
    return AuthService(cognito_client)
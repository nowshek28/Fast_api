from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.cognito import CognitoClient
from app.auth.jwt_verifier import JWTVerifier
from app.auth.schemas import TokenClaims
from app.auth.service import AuthService
from app.core.dependencies import get_user_service
from app.schemas.user import CurrentUserResponse, UserCreate
from app.services.user_service import UserService

security = HTTPBearer()

def get_cognito_client() -> CognitoClient:
    """
    Dependency to get an instance of CognitoClient.
    """
    return CognitoClient()

def get_jwt_verifier() -> JWTVerifier:
    return JWTVerifier()

def get_auth_service(cognito_client: CognitoClient = Depends(get_cognito_client),
                     jwt_verifier: JWTVerifier = Depends(get_jwt_verifier)) -> AuthService:
    """
    Dependency to get an instance of AuthService.
    """
    return AuthService(cognito_client, jwt_verifier)

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        verifier: JWTVerifier = Depends(get_jwt_verifier),
) -> TokenClaims:
    """
    Dependency to get the current authenticated user based on the provided JWT token.
    """
    token = credentials.credentials
    try:
        claims = verifier.verify_access_token(token)
    except (ValueError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenClaims(**claims)

def get_current_db_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        claims: TokenClaims = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
        cognito_client: CognitoClient = Depends(get_cognito_client),
) -> CurrentUserResponse:
    """
    Returns the DB record for the authenticated user, creating it on first login.
    The user's real name is fetched from Cognito via GetUser because the access
    token only carries the internal Cognito username (a UUID), not the 'name' attribute.
    """
    user = user_service.get_user_by_cognito_sub(claims.sub)
    if user is None:
        try:
            attrs = cognito_client.get_user_attributes(credentials.credentials)
            display_name = attrs.get("name") or attrs.get("email") or claims.username
        except Exception:
            display_name = claims.username
        user = user_service.create_user(
            UserCreate(cognito_sub=claims.sub, username=display_name)
        )
    return user
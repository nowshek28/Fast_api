from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_auth_service
from app.auth.exceptions import InvalidCredentialsError, UserNotConfirmedError
from app.auth.schemas import ConfirmSignUpResponse, ConfirmSignUpRequest, LoginRequest, LoginResponse, SignUpRequest, SignUpResponse
from app.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/signup",
    response_model=SignUpResponse,
    summary="Register a new user using AWS Cognito",
    response_description="Returns a message indicating the result of the sign-up operation"
)
def sign_up(
    sign_up_request: SignUpRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> SignUpResponse:
    """
    Register a new user using their email and password.
    
    Args:
        sign_up_request (SignUpRequest): The sign-up request containing email, password, and full name.
        auth_service (AuthService): The authentication service dependency.
        
    Returns:
        SignUpResponse: The response indicating the result of the sign-up operation.
    """
    # Always return the same response to prevent user enumeration
    try:
        return auth_service.sign_up(
            email=sign_up_request.email, 
            password=sign_up_request.password,
            name=sign_up_request.name
        )
    except InvalidCredentialsError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            # Return same shape as success to prevent email enumeration
            return SignUpResponse(message="If this email is not registered, a confirmation email has been sent.", user_confirmed=False)
        raise HTTPException(
            status_code=400,
            detail="Sign-up failed. Please check your input and try again."
        )
    

@router.post(
    "/confirm-signup",
    response_model=ConfirmSignUpResponse,
    summary="Confirm a user's sign-up using AWS Cognito",
    response_description="Returns a message indicating the result of the confirmation operation"
)
def confirm_sign_up(
    confirm_sign_up_request: ConfirmSignUpRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> ConfirmSignUpResponse:
    """
    Confirm a user's sign-up using their email and confirmation code.
    
    Args:
        confirm_sign_up_request (ConfirmSignUpRequest): The confirmation request containing email and confirmation code.
        auth_service (AuthService): The authentication service dependency.
        
    Returns:
        ConfirmSignUpResponse: The response indicating the result of the confirmation operation.
    """
    try:
        return auth_service.confirm_sign_up(
            email=confirm_sign_up_request.email, 
            confirmation_code=confirm_sign_up_request.confirmation_code
        )
    
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid confirmation code."
        )
    except UserNotConfirmedError:
        raise HTTPException(
            status_code=403, 
            detail="User account is not confirmed. Please check your email for confirmation instructions."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="authenticate user using AWS Cognito",
    response_description="Returns the authentication tokens upon successful login"
)
def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """
    Authenticate a user using their email and password.
    
    Args:
        login_request (LoginRequest): The login request containing email and password.
        auth_service (AuthService): The authentication service dependency.
        
    Returns:
        LoginResponse: The response containing authentication tokens.
    """

    try:
        return auth_service.login(
            email=login_request.email, 
            password=login_request.password
            )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password."
            )
    except UserNotConfirmedError:
        raise HTTPException(
            status_code=403, 
            detail="User account is not confirmed. Please check your email for confirmation instructions."
            )
    

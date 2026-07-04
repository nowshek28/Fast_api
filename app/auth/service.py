from app.auth.cognito import CognitoClient
from app.auth.schemas import ConfirmSignUpResponse, LoginResponse, SignUpResponse

class AuthService:

    def __init__(self, cognito_client: CognitoClient):
        """
        Initialize the AuthService with a Cognito client.
        """
        self.cognito_client = cognito_client

    def sign_up(self, email: str, password: str, name: str) -> SignUpResponse:
        """
        Sign up a new user using their email and password.
        Args:
            email (str): The user's email address.
            password (str): The user's password.
            name (str): The user's full name.
            
        Returns:
            SignUpResponse
        """
        response = self.cognito_client.sign_up(email=email, password=password, name=name)
        return SignUpResponse(
            message="User signed up successfully.",
            user_confirmed=response.get("UserConfirmed", False)
        )
    
    def confirm_sign_up(self, email: str, confirmation_code: str) -> ConfirmSignUpResponse:
        """
        Confirm a user's sign-up using their email and confirmation code.
        Args:
            email (str): The user's email address.
            confirmation_code (str): The confirmation code sent to the user's email.
    
        Returns:
            ConfirmSignUpResponse
        """
        response = self.cognito_client.confirm_sign_up(email=email, confirmation_code=confirmation_code)
        return response

    def login(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate a user using their email and password.
        Args:
            email (str): The user's email address.
            password (str): The user's password.
            
        Returns:
            LoginResponse
        """

        response = self.cognito_client.login(
            username=email, 
            password=password
            )
        
        authentication_response = response['AuthenticationResult']

        return LoginResponse(
            access_token=authentication_response['AccessToken'],
            refresh_token=authentication_response['RefreshToken'],
            id_token=authentication_response['IdToken'],
            expires_in=authentication_response['ExpiresIn'],
            token_type=authentication_response['TokenType']
        )
    

import base64
import hashlib
import hmac

import boto3

import logging

from app.auth.exceptions import InvalidCredentialsError, UserNotConfirmedError
from app.auth.schemas import ConfirmSignUpResponse, LoginResponse
from app.core.config import settings


class CognitoClient:

    def __init__(self):
        """
        Initialize the Cognito client.
        This client is responsible for interacting with AWS Cognito for user authentication.
        """
        self.client = boto3.client(
            "cognito-idp",
            region_name=settings.AWS_REGION,
        )

        self.logger = logging.getLogger(__name__)

    def _calculate_secret_hash(self, username: str) -> str:
        """
        Calculate the secret hash for Cognito.
        The message is the concatenation of the username and the client ID, and the key is the client secret. 
        The secret hash is then generated using HMAC with SHA256 and base64 encoding.
        """
        message = bytes(username + settings.COGNITO_CLIENT_ID, "utf-8")
        key = bytes(settings.COGNITO_CLIENT_SECRET, "utf-8")
        secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
        return secret_hash
    
    def sign_up(self, email: str, password: str, name: str) -> dict:
        """Sign up a new user in Cognito."""

        try:
            response = self.client.sign_up(
                ClientId=settings.COGNITO_CLIENT_ID,
                Username=email,
                Password=password,
                SecretHash=self._calculate_secret_hash(email),
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "name", "Value": name},
                ],
            )

            self.logger.info("User signed up successfully.")
            return response
        
        except self.client.exceptions.UsernameExistsException:
            self.logger.warning("Sign-up attempted with already registered email.")
            raise InvalidCredentialsError("User already exists.")
        
        except self.client.exceptions.InvalidPasswordException:
            self.logger.error("Sign-up failed: invalid password.")
            raise InvalidCredentialsError("Invalid password.")
        
        except self.client.exceptions.InvalidParameterException as e:
            self.logger.error(f"Invalid parameter during sign_up: {e}")
            raise InvalidCredentialsError("Sign-up failed due to invalid parameters.")

    def confirm_sign_up(self, email: str, confirmation_code: str) -> ConfirmSignUpResponse:
        """Confirm a new user's sign-up in Cognito."""
        try:
            response = self.client.confirm_sign_up(
                ClientId=settings.COGNITO_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                SecretHash=self._calculate_secret_hash(email),
            )
            self.logger.info("User confirmed successfully.")
            return ConfirmSignUpResponse(message="User confirmed successfully.")
        except self.client.exceptions.UserNotFoundException:
            self.logger.error("Confirmation failed: user not found.")
            raise InvalidCredentialsError("User not found.")
        except self.client.exceptions.CodeMismatchException:
            self.logger.error("Confirmation failed: invalid confirmation code.")
            raise InvalidCredentialsError("Invalid confirmation code.")
        except self.client.exceptions.ExpiredCodeException:
            self.logger.error("Confirmation failed: confirmation code expired.")
            raise InvalidCredentialsError("Confirmation code expired.")

    def login(self, username: str, password: str) -> LoginResponse:
        """Log in a user in Cognito."""

        try:

            response = self.client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password,
                    "SECRET_HASH": self._calculate_secret_hash(username),
                }
            )
            
            self.logger.info("User logged in successfully.")

            return response

        except self.client.exceptions.NotAuthorizedException:
            self.logger.warning("Login failed: invalid credentials.")
            raise InvalidCredentialsError("Invalid username or password.")
        
        except self.client.exceptions.UserNotConfirmedException:
            self.logger.warning("Login failed: user not confirmed.")
            raise UserNotConfirmedError("User is not confirmed. Please confirm your account before logging in.")
        
        except self.client.exceptions.UserNotFoundException:
            self.logger.warning("Login failed: user not found.")
            raise InvalidCredentialsError("Invalid username or password.")
        

        

    def refresh_token(self):
        """Refresh a user's Cognito token."""
        pass
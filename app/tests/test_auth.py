import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.auth.dependencies import get_auth_service
from app.auth.service import AuthService
from app.tests.fakes import FakeCognitoClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_client():
    """
    TestClient with AWS Cognito replaced by FakeCognitoClient.
    A fresh fake is created per test so state never leaks between tests.
    Returns (client, fake_cognito) so tests can pre-seed users when needed.
    """
    fake_cognito = FakeCognitoClient()

    def override_get_auth_service() -> AuthService:
        return AuthService(fake_cognito)

    app.dependency_overrides[get_auth_service] = override_get_auth_service
    yield TestClient(app), fake_cognito
    app.dependency_overrides.pop(get_auth_service, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_SIGNUP_PAYLOAD = {
    "email": "test@example.com",
    "password": "SecurePass1!",
    "name": "Test User",
}

VALID_LOGIN_PAYLOAD = {
    "email": "test@example.com",
    "password": "SecurePass1!",
}


def _register_and_confirm(fake: FakeCognitoClient, email: str, password: str, name: str = "Test User"):
    """Pre-seed the fake with a confirmed user (skips HTTP layer)."""
    fake.sign_up(email=email, password=password, name=name)
    fake.confirm_sign_up(email=email, confirmation_code=FakeCognitoClient.VALID_CONFIRMATION_CODE)


# ---------------------------------------------------------------------------
# POST /auth/signup
# ---------------------------------------------------------------------------

def test_signup_success(auth_client):
    client, _ = auth_client
    response = client.post("/auth/signup", json=VALID_SIGNUP_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "user_confirmed" in data
    assert data["user_confirmed"] is False


def test_signup_duplicate_email_does_not_reveal_existence(auth_client):
    """Signing up with an existing email must return the same shape as success (no enumeration)."""
    client, fake = auth_client
    # Pre-seed a user directly so the email is already taken
    fake.sign_up(email="existing@example.com", password="Pass1234!", name="Existing")

    response = client.post("/auth/signup", json={**VALID_SIGNUP_PAYLOAD, "email": "existing@example.com"})
    assert response.status_code == 200
    data = response.json()
    # Generic message — does NOT say "user already exists"
    assert "message" in data
    assert "already exists" not in data["message"].lower()


def test_signup_invalid_email_format(auth_client):
    client, _ = auth_client
    response = client.post("/auth/signup", json={**VALID_SIGNUP_PAYLOAD, "email": "not-an-email"})
    assert response.status_code == 422


def test_signup_password_too_short(auth_client):
    client, _ = auth_client
    response = client.post("/auth/signup", json={**VALID_SIGNUP_PAYLOAD, "password": "short"})
    assert response.status_code == 422


def test_signup_password_too_long(auth_client):
    client, _ = auth_client
    response = client.post("/auth/signup", json={**VALID_SIGNUP_PAYLOAD, "password": "A" * 129})
    assert response.status_code == 422


def test_signup_name_too_long(auth_client):
    client, _ = auth_client
    response = client.post("/auth/signup", json={**VALID_SIGNUP_PAYLOAD, "name": "A" * 101})
    assert response.status_code == 422


def test_signup_missing_name(auth_client):
    client, _ = auth_client
    payload = {"email": "test@example.com", "password": "SecurePass1!"}
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/confirm-signup
# ---------------------------------------------------------------------------

def test_confirm_signup_success(auth_client):
    client, fake = auth_client
    fake.sign_up(email="test@example.com", password="SecurePass1!", name="Test User")

    response = client.post("/auth/confirm-signup", json={
        "email": "test@example.com",
        "confirmation_code": FakeCognitoClient.VALID_CONFIRMATION_CODE,
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_confirm_signup_wrong_code(auth_client):
    client, fake = auth_client
    fake.sign_up(email="test@example.com", password="SecurePass1!", name="Test User")

    response = client.post("/auth/confirm-signup", json={
        "email": "test@example.com",
        "confirmation_code": "000000",
    })
    assert response.status_code == 400


def test_confirm_signup_invalid_code_format(auth_client):
    """Confirmation code must be exactly 6 digits — schema-level validation."""
    client, _ = auth_client
    response = client.post("/auth/confirm-signup", json={
        "email": "test@example.com",
        "confirmation_code": "ABC123",  # not all digits
    })
    assert response.status_code == 422


def test_confirm_signup_user_not_found(auth_client):
    client, _ = auth_client
    response = client.post("/auth/confirm-signup", json={
        "email": "ghost@example.com",
        "confirmation_code": FakeCognitoClient.VALID_CONFIRMATION_CODE,
    })
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

def test_login_success(auth_client):
    client, fake = auth_client
    _register_and_confirm(fake, "test@example.com", "SecurePass1!")

    response = client.post("/auth/login", json=VALID_LOGIN_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "fake-access-token"
    assert data["id_token"] == "fake-id-token"
    assert data["refresh_token"] == "fake-refresh-token"
    assert data["expires_in"] == 3600
    assert data["token_type"] == "Bearer"


def test_login_wrong_password(auth_client):
    client, fake = auth_client
    _register_and_confirm(fake, "test@example.com", "SecurePass1!")

    response = client.post("/auth/login", json={**VALID_LOGIN_PAYLOAD, "password": "WrongPass1!"})
    assert response.status_code == 401


def test_login_unconfirmed_user(auth_client):
    """Login must be rejected with 403 when the user hasn't confirmed their account."""
    client, fake = auth_client
    # Sign up but do NOT confirm
    fake.sign_up(email="test@example.com", password="SecurePass1!", name="Test User")

    response = client.post("/auth/login", json=VALID_LOGIN_PAYLOAD)
    assert response.status_code == 403


def test_login_nonexistent_user(auth_client):
    client, _ = auth_client
    response = client.post("/auth/login", json=VALID_LOGIN_PAYLOAD)
    assert response.status_code == 401


def test_login_invalid_email_format(auth_client):
    client, _ = auth_client
    response = client.post("/auth/login", json={"email": "bad-email", "password": "SecurePass1!"})
    assert response.status_code == 422


def test_login_missing_password(auth_client):
    client, _ = auth_client
    response = client.post("/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422

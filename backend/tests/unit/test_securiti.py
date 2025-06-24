from jose import jwt
from datetime import timedelta, timezone, datetime
from backend.src.config.settings import settings
from backend.src.utils.security import create_access_token, create_refresh_token
from uuid import UUID
from backend.src.utils.security import verify_password
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestTokenCreation:
    def test_create_access_token_contains_expected_fields(self):
        """Test access token creation and verify expected JWT fields."""
        payload = {"sub": "user@example.com", "user_id": 123}
        token = create_access_token(payload, expires_delta=timedelta(minutes=5))

        assert isinstance(token, str)
        assert token != ""

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded["sub"] == "user@example.com"
        assert decoded["user_id"] == 123
        assert decoded["token_type"] == "access"
        assert "exp" in decoded

        assert datetime.fromtimestamp(decoded["exp"], tz=timezone.utc) > datetime.now(timezone.utc)

    def test_create_refresh_token_contains_expected_fields(self):
        """Test refresh token creation and verify expected JWT fields."""
        payload = {"sub": "user@example.com", "user_id": 123}
        token = create_refresh_token(payload, expires_delta=timedelta(days=1))

        assert isinstance(token, str)
        assert token != ""

        decoded = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert decoded["sub"] == "user@example.com"
        assert decoded["user_id"] == 123
        assert decoded["token_type"] == "refresh"
        assert "exp" in decoded
        assert "jti" in decoded

        jti = decoded["jti"]
        uuid_obj = UUID(jti, version=4)
        assert str(uuid_obj) == jti
        assert datetime.fromtimestamp(decoded["exp"], tz=timezone.utc) > datetime.now(timezone.utc)


class TestPasswordVerification:

    def test_verify_password_success(self):
        """Verify that correct password matches the hashed password."""
        plain = "supersecret"
        hashed = pwd_context.hash(plain)

        assert verify_password(plain, hashed) is True

    def test_verify_password_failure(self):
        """Verify that incorrect password does not match the hashed password."""
        plain = "supersecret"
        wrong = "notthis"
        hashed = pwd_context.hash(plain)

        assert verify_password(wrong, hashed) is False

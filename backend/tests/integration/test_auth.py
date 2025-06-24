import pytest
from fastapi import HTTPException
from backend.src.models import TeamRole
from backend.src.services.auth import get_current_user, decode_refresh_token
from backend.src.utils.security import create_refresh_token, create_access_token


@pytest.mark.asyncio
class TestAuthDependencies:

    async def test_get_current_user_valid_token(self):
        """Return user info for valid access token."""
        token = create_access_token({
            "sub": "1",
            "role": "admin",
            "teams": [{"team_id": 10, "role": "manager"}],
        })

        class DummyCreds:
            credentials = token

        user = await get_current_user(token=DummyCreds())

        assert user.id == 1
        assert user.role == "admin"
        assert len(user.teams) == 1
        assert user.teams[0].team_id == 10
        assert user.teams[0].role == TeamRole.MANAGER

    async def test_get_current_user_with_refresh_token_raises(self):
        """Raise HTTPException when using refresh token as access token."""
        token = create_refresh_token({
            "sub": "1",
            "role": "admin",
            "teams": [{"team_id": 10, "role": "manager"}]
        })

        class DummyCreds:
            credentials = token

        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=DummyCreds())
        assert exc.value.status_code == 401

    async def test_get_current_user_invalid_token_raises(self):
        """Raise HTTPException for malformed token."""

        class DummyCreds:
            credentials = "invalid.token.structure"

        with pytest.raises(HTTPException):
            await get_current_user(token=DummyCreds())

    async def test_decode_refresh_token_valid(self):
        """Return payload for valid refresh token."""
        token = create_refresh_token({
            "sub": "1",
            "role": "user",
            "teams": [{"team_id": 5, "role": "EXECUTOR"}],
            "jti": "abcd1234"
        })

        payload = await decode_refresh_token(token)

        assert payload["user_id"] == 1
        assert payload["role"] == "user"
        assert payload["teams"][0]["team_id"] == 5

    async def test_decode_refresh_token_invalid_raises(self):
        """Raise HTTPException for invalid refresh token."""
        token = "invalid.token"

        with pytest.raises(HTTPException):
            await decode_refresh_token(token)

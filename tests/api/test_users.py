import pytest
from httpx import AsyncClient
from fastapi import HTTPException
from src.deps.permissions import is_admin
from src.services.auth import get_current_user
from src.main import app


@pytest.mark.asyncio
class TestUserAPI:

    async def test_create_user_success(self, test_client: AsyncClient, user_data):
        """Test creating a user successfully returns 201."""
        response = await test_client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "password" not in data

    async def test_create_user_duplicate_email(self, test_client: AsyncClient, user_data):
        """Test creating a user with duplicate email returns 400."""
        response1 = await test_client.post("/users/", json=user_data)
        assert response1.status_code == 201

        response2 = await test_client.post("/users/", json=user_data)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Email already registered"

    async def test_read_users_as_admin(self, test_client: AsyncClient, admin_user_payload):
        """Test getting all users as an admin. Should return 200 and list of users."""

        async def override_is_admin():
            return admin_user_payload

        app.dependency_overrides[is_admin] = override_is_admin

        response = await test_client.get("/users/")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

        app.dependency_overrides.clear()

    async def test_read_users_as_non_admin(self, test_client, normal_user_payload):
        """Test that non-admin users cannot access the endpoint. Should return 403 Forbidden."""

        async def override_is_admin():
            raise HTTPException(status_code=403, detail="Not admin")

        app.dependency_overrides[is_admin] = override_is_admin

        response = await test_client.get("/users/")
        assert response.status_code == 403

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUserProfileAPI:

    async def test_update_own_profile_success(self, test_client: AsyncClient, normal_user_payload, user_data):
        """Test updating current user's profile."""

        async def override_get_current_user():
            return normal_user_payload

        app.dependency_overrides[get_current_user] = override_get_current_user

        update_data = {"first_name": "UpdatedName"}

        response = await test_client.put("/users/me", json=update_data)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["first_name"] == update_data["first_name"]
        assert updated_user["email"] == user_data["email"]

        app.dependency_overrides.clear()

    async def test_read_user_detail_admin_success(self, test_client, admin_user_payload, user_data):
        """Test get user detail as admin user."""

        async def override_get_current_user():
            return admin_user_payload

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await test_client.post("/users/", json=user_data)
        assert response.status_code == 201
        created_user = response.json()
        user_id = created_user["id"]

        response = await test_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        user_detail = response.json()
        assert user_detail["id"] == user_id
        assert "teams" in user_detail

        app.dependency_overrides.clear()


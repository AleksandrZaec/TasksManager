import pytest
from httpx import AsyncClient
from fastapi import status
from src.deps.permissions import is_admin, is_admin_and_member
from src.main import app
from src.schemas import TeamCreate, TeamRead
from src.models import UserRole, Team
from src.services.team import teams_crud
from sqlalchemy import select


@pytest.mark.asyncio
class TestTeamAPI:

    async def test_create_team_success(self, test_client: AsyncClient, admin_user_payload, admin_user_in_db):
        """Test successful creation of a new team by an admin user."""

        async def override_is_admin():
            return admin_user_payload

        app.dependency_overrides[is_admin] = override_is_admin

        team_data = {
            "name": "New Team",
            "description": "A test team",
            "invite_code_expires_at": None,
            "users": []
        }

        response = await test_client.post("/teams/", json=team_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == team_data["name"]
        assert "id" in data

        app.dependency_overrides.clear()

    async def test_create_team_duplicate_name(self, test_client: AsyncClient, admin_user_payload, admin_user_in_db):
        """Test that creating a team with a duplicate name fails."""

        async def override_is_admin():
            return admin_user_payload

        app.dependency_overrides[is_admin] = override_is_admin

        team_data = {
            "name": "Duplicate Team",
            "description": "A test team",
            "users": []
        }

        response1 = await test_client.post("/teams/", json=team_data)
        assert response1.status_code == status.HTTP_201_CREATED

        response2 = await test_client.post("/teams/", json=team_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"]

        app.dependency_overrides.clear()

    async def test_create_team_non_admin_forbidden(self, test_client: AsyncClient, normal_user_payload):
        """Test that a non-admin user cannot create a team."""

        async def override_is_admin():
            from fastapi import HTTPException
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_admin] = override_is_admin

        team_data = {
            "name": "Forbidden Team",
            "description": "Should not be created",
            "users": []
        }

        response = await test_client.post("/teams/", json=team_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestReadTeamsAllAPI:

    async def test_read_teams_all_as_admin(self, test_client: AsyncClient, admin_user_payload, admin_user_in_db,
                                           test_session):
        """Admin user can retrieve a list of all teams."""

        async def override_is_admin():
            return admin_user_payload

        app.dependency_overrides[is_admin] = override_is_admin

        team1 = TeamCreate(name="Team 1", description="Desc 1")
        team2 = TeamCreate(name="Team 2", description="Desc 2")

        await teams_crud.create_team(test_session, team1, admin_user_payload.id)
        await teams_crud.create_team(test_session, team2, admin_user_payload.id)

        response = await test_client.get("/teams/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        names = [team["name"] for team in data]
        assert "Team 1" in names
        assert "Team 2" in names

        app.dependency_overrides.clear()

    async def test_read_teams_all_as_non_admin_forbidden(self, test_client: AsyncClient, normal_user_payload):
        """Non-admin user receives 403 Forbidden when accessing the teams list."""

        async def override_is_admin():
            from fastapi import HTTPException
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_admin] = override_is_admin

        response = await test_client.get("/teams/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestDeleteTeamAPI:

    async def test_delete_team_success(self, test_client: AsyncClient, admin_user_payload, admin_user_in_db,
                                       test_session):
        """Admin and team member can successfully delete a team."""

        async def override_is_admin_and_member():
            return admin_user_payload

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        team_in = TeamCreate(name="TeamToDelete", description="To be deleted")
        team = await teams_crud.create_team(test_session, team_in, admin_user_payload.id)

        response = await test_client.delete(f"/teams/{team.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        result = await test_session.execute(select(Team).where(Team.id == team.id))
        deleted_team = result.scalar_one_or_none()
        assert deleted_team is None

        app.dependency_overrides.clear()

    async def test_delete_team_forbidden_for_non_admin(self, test_client: AsyncClient, normal_user_payload):
        """Non-admin or non-team member receives 403 Forbidden when trying to delete a team."""

        async def override_is_admin_and_member():
            from fastapi import HTTPException
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        response = await test_client.delete("/teams/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()

    async def test_delete_nonexistent_team(self, test_client: AsyncClient, admin_user_payload):
        """Deleting a non-existent team should raise a 404 error."""

        async def override_is_admin_and_member():
            return admin_user_payload

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        response = await test_client.delete("/teams/999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUpdateTeamAPI:

    async def test_update_team_success(self, test_client: AsyncClient, admin_user_payload, admin_user_in_db,
                                       test_session):
        """Admin and team member can successfully update a team's details."""

        async def override_is_admin_and_member():
            return admin_user_payload

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        team_in = TeamCreate(name="TeamToUpdate", description="Initial desc")
        team = await teams_crud.create_team(test_session, team_in, admin_user_payload.id)

        update_data = {
            "name": "Updated Team Name",
            "description": "Updated description"
        }

        response = await test_client.put(f"/teams/{team.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == team.id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

        app.dependency_overrides.clear()

    async def test_update_team_forbidden_for_non_admin(self, test_client: AsyncClient, normal_user_payload):
        """Non-admin or non-team member cannot update a team."""

        async def override_is_admin_and_member():
            from fastapi import HTTPException
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        update_data = {
            "name": "Should Not Update",
            "description": "No access"
        }

        response = await test_client.put("/teams/1", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()

    async def test_update_nonexistent_team(self, test_client: AsyncClient, admin_user_payload):
        """Updating a non-existent team should return 404."""

        async def override_is_admin_and_member():
            return admin_user_payload

        app.dependency_overrides[is_admin_and_member] = override_is_admin_and_member

        update_data = {
            "name": "Nonexistent Team",
            "description": "Does not exist"
        }

        response = await test_client.put("/teams/999999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        app.dependency_overrides.clear()

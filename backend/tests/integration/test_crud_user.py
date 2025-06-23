import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from backend.src.models import TeamRole, TeamUserAssociation, User
from backend.src.schemas import UserUpdate, UserCreate
from backend.src.schemas.team import TeamCreate
from backend.src.models.enum import UserRole


@pytest.mark.asyncio
class TestUserCRUDCreate:
    async def test_create_user_success(self, test_session, users_crud):
        """Test successful user creation with valid data."""
        user_in = UserCreate(
            email="newuser@example.com",
            password="Password123!",
            first_name="New",
            last_name="User"
        )
        user = await users_crud.create(test_session, user_in)

        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert hasattr(user, "id")
        assert not hasattr(user, "password")

    async def test_create_user_duplicate_email(self, test_session, create_user, users_crud):
        """Test that creating a user with duplicate email raises HTTP 400."""
        await create_user(email="duplicate@example.com")

        user_in = UserCreate(
            email="duplicate@example.com",
            password="AnotherPass123!",
            first_name="Dup",
            last_name="User"
        )

        with pytest.raises(HTTPException) as exc_info:
            await users_crud.create(test_session, user_in)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail


@pytest.mark.asyncio
class TestUserCRUDUpdate:
    async def test_update_user_name(self, test_session, create_user, users_crud):
        """Test updating user's first and last name."""
        user = await create_user(email="user1@example.com")
        update = UserUpdate(first_name="New", last_name="User")

        updated = await users_crud.update(test_session, user.id, update)

        assert updated.first_name == "New"
        assert updated.last_name == "User"

    async def test_update_user_email_success(self, test_session, create_user, users_crud):
        """Test successful update of user's email."""
        user = await create_user(email="user2@example.com")
        update = UserUpdate(email="newemail@example.com")

        updated = await users_crud.update(test_session, user.id, update)
        assert updated.email == "newemail@example.com"

    async def test_update_user_email_duplicate(self, test_session, create_user, users_crud):
        """Test that updating email to one already used raises HTTP 400."""
        await create_user(email="existing@example.com")
        user2 = await create_user(email="target@example.com")

        update = UserUpdate(email="existing@example.com")
        with pytest.raises(HTTPException) as exc_info:
            await users_crud.update(test_session, user2.id, update)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail


@pytest.mark.asyncio
class TestUserCRUDGetForLogin:
    async def test_get_for_login_user_not_found(self, test_session, users_crud):
        """Test get_for_login returns None if user not found."""
        result = await users_crud.get_for_login(test_session, "missing@example.com")
        assert result is None

    async def test_get_for_login_user_found(self, test_session, create_user, create_team, users_crud):
        """Test get_for_login returns correct user data with teams and roles."""
        user = await create_user(email="login@example.com")
        team = await create_team(name="Login Team", creator_id=user.id)

        result = await users_crud.get_for_login(test_session, email=user.email)

        assert result["id"] == user.id
        assert "password" in result
        assert any(t["team_id"] == team.id and t["role"] == TeamRole.MANAGER.value for t in result["teams"])


@pytest.mark.asyncio
class TestGetWithTeams:
    async def test_user_found_with_teams(self, test_session, create_user, create_team, users_crud):
        """Test retrieving user with their teams and roles."""
        user = await create_user(email="withteams@example.com")
        team = await create_team(name="Team A", creator_id=user.id)

        result = await users_crud.get_with_teams(test_session, user.id)

        assert result.id == user.id
        assert len(result.teams) == 1
        assert result.teams[0].team_id == team.id
        assert result.teams[0].role == TeamRole.MANAGER

    async def test_user_found_without_teams(self, test_session, create_user, users_crud):
        """Test retrieving user who belongs to no teams."""
        user = await create_user(email="noteams@example.com")

        result = await users_crud.get_with_teams(test_session, user.id)

        assert result.teams == []

    async def test_user_not_found(self, test_session, users_crud):
        """Test get_with_teams raises 404 if user not found."""
        with pytest.raises(HTTPException) as exc_info:
            await users_crud.get_with_teams(test_session, user_id=999999)

        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestSetGlobalRole:
    async def test_success(self, test_session, create_user, users_crud):
        """Test successful update of global user role."""
        user = await create_user(email="changerole@example.com")
        updated = await users_crud.set_global_role(test_session, user.id, UserRole.ADMIN)

        assert updated.role == UserRole.ADMIN

        result = await test_session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one()
        assert db_user.role == UserRole.ADMIN

    async def test_user_not_found(self, test_session, users_crud):
        """Test set_global_role raises 404 if user not found."""
        with pytest.raises(HTTPException) as exc_info:
            await users_crud.set_global_role(test_session, user_id=999999, role=UserRole.ADMIN)

        assert exc_info.value.status_code == 404

    async def test_db_error(self, test_session, create_user, users_crud, monkeypatch):
        """Test database commit failure raises 500 error."""
        user = await create_user(email="erroruser@example.com")

        async def fake_commit():
            raise Exception("forced commit error")

        monkeypatch.setattr(test_session, "commit", fake_commit)

        with pytest.raises(HTTPException) as exc_info:
            await users_crud.set_global_role(test_session, user.id, UserRole.ADMIN)

        assert exc_info.value.status_code == 500
        assert "Database error: forced commit error" in exc_info.value.detail


@pytest.mark.asyncio
class TestUserCRUDGetTeamUsers:

    async def test_team_has_no_users(self, test_session: AsyncSession, team_crud, users_crud):
        """Test that get_team_users returns empty list if no users in team."""
        team_in = TeamCreate(name="Empty Team", description="No users")
        team = await team_crud.create_team(test_session, team_in=team_in, creator_id=None)

        users = await users_crud.get_team_users(test_session, team.id)
        assert users == []

    async def test_team_has_multiple_users(self, test_session: AsyncSession, create_user, create_team, users_crud):
        """Test get_team_users returns all users associated with team."""
        creator = await create_user(email="creator@example.com")
        team = await create_team(name="Dev Team", creator_id=creator.id)

        member1 = await create_user(email="member1@example.com")
        member2 = await create_user(email="member2@example.com")

        association1 = TeamUserAssociation(user_id=member1.id, team_id=team.id, role=TeamRole.EXECUTOR)
        association2 = TeamUserAssociation(user_id=member2.id, team_id=team.id, role=TeamRole.MANAGER)

        test_session.add_all([association1, association2])
        await test_session.commit()

        users = await users_crud.get_team_users(test_session, team.id)

        emails = {user.email for user in users}
        assert "member1@example.com" in emails
        assert "member2@example.com" in emails
        assert len(users) == 3

    async def test_nonexistent_team_returns_empty(self, test_session: AsyncSession, users_crud):
        """Test get_team_users returns empty list for non-existent team."""
        users = await users_crud.get_team_users(test_session, 999999)
        assert users == []

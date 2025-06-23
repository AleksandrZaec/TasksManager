import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.services.user import UserCRUD
from backend.src.services.team import TeamCRUD
from backend.src.schemas import UserCreate, TeamCreate


@pytest.fixture(scope="session")
def users_crud():
    """Provide UserCRUD instance."""
    return UserCRUD()


@pytest.fixture(scope="session")
def team_crud():
    """Provide TeamCRUD instance."""
    return TeamCRUD()


@pytest.fixture
async def create_user(test_session: AsyncSession, users_crud):
    """Factory fixture to create a user with default or given parameters."""

    async def _create_user(
            email="user@example.com",
            password="Password123!",
            first_name="First",
            last_name="Last"
    ):
        user_in = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user = await users_crud.create(test_session, user_in)
        return user

    return _create_user


@pytest.fixture
async def create_team(test_session: AsyncSession, team_crud, create_user):
    """Factory fixture to create a team with optional creator and user list."""

    async def _create_team(
            name="Test Team",
            description="Description",
            creator_id=None,
            users=None
    ):
        if creator_id is None:
            creator = await create_user()
            creator_id = creator.id

        users = users or []

        team_in = TeamCreate(name=name, description=description, users=users)
        team = await team_crud.create_team(test_session, team_in, creator_id=creator_id)
        return team

    return _create_team

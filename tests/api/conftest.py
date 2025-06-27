import pytest
import pytest_asyncio
from src.schemas.user import UserPayload, UserRole, UserTeamInfo, TeamRole
from src.models import User, Team, TaskPriority, TaskStatus, Task
from src.utils.security import pwd_context


@pytest.fixture
def user_data():
    """Provide valid user data for creating a user."""
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "StrongPass!1"
    }


@pytest.fixture
def admin_user_payload():
    """Return a UserPayload with ADMIN role for auth override."""
    return UserPayload(
        id=1,
        role=UserRole.ADMIN.value,
        teams=[UserTeamInfo(team_id=1, role=TeamRole.MANAGER)]
    )


@pytest_asyncio.fixture
async def normal_user_payload(test_session, test_client, user_data):
    """Return a UserPayload with USER role for auth override."""
    response = await test_client.post("/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    payload = UserPayload(
        id=created_user["id"],
        role="user",
        teams=[]
    )
    yield payload


@pytest_asyncio.fixture
async def admin_user_in_db(test_session):
    """Create and persist an admin user in the test database."""
    admin_user = User(
        email="admin@example.com",
        password=pwd_context.hash("StrongPass!1"),
        role="admin",
        first_name="Admin",
        last_name="User"
    )
    test_session.add(admin_user)
    await test_session.commit()
    await test_session.refresh(admin_user)
    return admin_user


@pytest.fixture
async def admin_manager_payload():
    return UserPayload(id=1, role='ADMIN', email='admin@example.com')


@pytest.fixture
async def admin_manager_in_db(test_session):
    user = User(
        email="admin_manager@example.com",
        password=pwd_context.hash("strong_password"),
        first_name="Admin",
        last_name="Manager",
        role="ADMIN",
        is_active=True,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def team_in_db(test_session):
    team = Team(name="Test Team", description="desc", invite_code="TEST123")
    test_session.add(team)
    await test_session.commit()
    await test_session.refresh(team)
    return team


@pytest_asyncio.fixture
async def user_in_db(test_session):
    user = User(
        id=1,
        email="admin@example.com",
        role="ADMIN",
        first_name="Admin",
        last_name="User",
        password=pwd_context.hash("somehash"),
        is_active=True,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def create_task(test_session, user_in_db, team_in_db):
    task_data = {
        "title": "Initial Task",
        "description": "Test task description",
        "priority": TaskPriority.MEDIUM,
        "status": TaskStatus.OPEN,
        "creator_id": user_in_db.id,
        "team_id": team_in_db.id,
    }
    task = Task(**task_data)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task

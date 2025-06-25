import pytest
from httpx import AsyncClient
from fastapi import status, HTTPException
from src.main import app
from src.schemas.user import UserPayload
from src.deps.permissions import admin_manager_in_team, is_team_member
from src.services.auth import get_current_user


@pytest.mark.asyncio
class TestTaskCreation:

    async def test_create_task_success(self, test_client: AsyncClient, team_in_db, user_in_db):
        """Test successful task creation with valid data and permissions."""
        user = user_in_db
        team = team_in_db

        async def override_admin_manager_in_team(team_id: int):
            if team_id == team.id:
                return UserPayload(
                    id=user.id,
                    role="admin",
                    email=user.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_data = {
            "title": "New Task",
            "description": "Task desc",
            "priority": "medium",
            "status": "open",
            "assignees": []
        }
        response = await test_client.post(f"/tasks/{team.id}/tasks/", json=task_data)
        print(response.text)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == task_data["title"]
        assert "id" in data

        app.dependency_overrides.clear()

    async def test_create_task_with_duplicate_assignees_fails(self, test_client: AsyncClient, team_in_db, user_in_db):
        """Test that creating a task with duplicate assignees returns 422 error."""
        user = user_in_db
        team = team_in_db

        async def override_admin_manager_in_team(team_id: int):
            if team_id == team.id:
                return UserPayload(
                    id=user.id,
                    role="admin",
                    email=user.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        assignees = [
            {"user_id": 2, "role": "executor"},
            {"user_id": 2, "role": "executor"},
        ]
        task_data = {
            "title": "Task with duplicate assignees",
            "assignees": assignees
        }
        response = await test_client.post(f"/tasks/{team.id}/tasks/", json=task_data)
        assert response.status_code == 422
        assert "Duplicate user_id in assignees" in response.text

        app.dependency_overrides.clear()

    async def test_create_task_user_not_in_team_fails(self, test_client: AsyncClient, team_in_db, user_in_db):
        """Test that assigning a user not in the team returns a 400 error."""
        user = user_in_db
        team = team_in_db

        async def override_admin_manager_in_team(team_id: int):
            if team_id == team.id:
                return UserPayload(
                    id=user.id,
                    role="admin",
                    email=user.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        assignees = [
            {"user_id": 999, "role": "executor"}
        ]
        task_data = {
            "title": "Task with invalid assignee",
            "assignees": assignees
        }
        response = await test_client.post(f"/tasks/{team.id}/tasks/", json=task_data)
        assert response.status_code == 400
        assert "Users not found or not in team" in response.text

        app.dependency_overrides.clear()

    async def test_create_task_unauthorized_fails(self, test_client: AsyncClient, team_in_db):
        """Test that unauthorized users cannot create tasks (403 error)."""
        team = team_in_db

        async def override_admin_manager_in_team(team_id: int):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_data = {
            "title": "Unauthorized Task",
        }
        response = await test_client.post(f"/tasks/{team.id}/tasks/", json=task_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()

    async def test_create_task_missing_title_fails(self, test_client: AsyncClient, team_in_db, user_in_db):
        """Test that missing title in task creation returns validation error 422."""
        user = user_in_db
        team = team_in_db

        async def override_admin_manager_in_team(team_id: int):
            if team_id == team.id:
                return UserPayload(
                    id=user.id,
                    role="admin",
                    email=user.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_data = {
            "description": "No title task"
        }
        response = await test_client.post(f"/tasks/{team.id}/tasks/", json=task_data)
        assert response.status_code == 422

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUpdateTask:

    async def test_update_task_success(self, test_client: AsyncClient, team_in_db, user_in_db, create_task):
        """Test successful update of a task by an admin or manager in the team."""
        async def override_admin_manager_in_team(team_id: int):
            if team_id == team_in_db.id:
                return UserPayload(
                    id=user_in_db.id,
                    role="admin",
                    email=user_in_db.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "priority": "high",
            "status": "in_progress",
            "assignees": []
        }
        response = await test_client.put(
            f"/tasks/{team_in_db.id}/{create_task.id}",
            json=task_update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == task_update_data["title"]

        app.dependency_overrides.clear()

    async def test_update_task_unauthorized(self, test_client: AsyncClient, team_in_db, create_task):
        """Test that unauthorized users cannot update a task (403 Forbidden)."""
        async def override_admin_manager_in_team(team_id: int):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_update_data = {
            "title": "Attempted Unauthorized Update"
        }
        response = await test_client.put(
            f"/tasks/{team_in_db.id}/{create_task.id}",
            json=task_update_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()

    async def test_update_task_invalid_task_id(self, test_client: AsyncClient, team_in_db, user_in_db):
        """Test updating a task that does not exist returns 404 or appropriate error."""
        async def override_admin_manager_in_team(team_id: int):
            if team_id == team_in_db.id:
                return UserPayload(
                    id=user_in_db.id,
                    role="admin",
                    email=user_in_db.email,
                    teams=[{"team_id": team_id, "role": "manager"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[admin_manager_in_team] = override_admin_manager_in_team

        task_update_data = {
            "title": "Update Nonexistent Task"
        }
        invalid_task_id = 999999

        response = await test_client.put(
            f"/tasks/{team_in_db.id}/{invalid_task_id}",
            json=task_update_data
        )
        assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST)

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestGetTasksForTeam:

    async def test_get_tasks_for_team_success(self, test_client: AsyncClient, team_in_db, user_in_db, create_task):
        """Test retrieving tasks for a team successfully with valid membership."""
        async def override_is_team_member(team_id: int):
            if team_id == team_in_db.id:
                return UserPayload(
                    id=user_in_db.id,
                    role="user",
                    email=user_in_db.email,
                    teams=[{"team_id": team_id, "role": "executor"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_team_member] = override_is_team_member

        response = await test_client.get(f"/tasks/{team_in_db.id}/tasks")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "title" in data[0]
            assert "status" in data[0]

        app.dependency_overrides.clear()

    async def test_get_tasks_for_team_with_filters(self, test_client: AsyncClient, team_in_db, user_in_db, create_task):
        """Test retrieving tasks for a team with status and priority filters."""
        async def override_is_team_member(team_id: int):
            if team_id == team_in_db.id:
                return UserPayload(
                    id=user_in_db.id,
                    role="user",
                    email=user_in_db.email,
                    teams=[{"team_id": team_id, "role": "executor"}]
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_team_member] = override_is_team_member

        params = {
            "statuses": ["open", "in_progress"],
            "priorities": ["high"]
        }
        response = await test_client.get(f"/tasks/{team_in_db.id}/tasks", params=params)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

        app.dependency_overrides.clear()

    async def test_get_tasks_for_team_unauthorized(self, test_client: AsyncClient, team_in_db):
        """Test that unauthorized user cannot retrieve tasks (403 Forbidden)."""
        async def override_is_team_member(team_id: int):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        app.dependency_overrides[is_team_member] = override_is_team_member

        response = await test_client.get(f"/tasks/{team_in_db.id}/tasks")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestGetMyTasks:

    async def test_get_my_tasks_success(self, test_client: AsyncClient, user_in_db, create_task):
        """Test successful retrieval of tasks related to current user without filters."""
        async def override_get_current_user():
            return user_in_db

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await test_client.post("/tasks/my", json={})
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "title" in data[0]
            assert "status" in data[0]

        app.dependency_overrides.clear()

    async def test_get_my_tasks_with_filters(self, test_client: AsyncClient, user_in_db, create_task):
        """Test retrieval of tasks related to current user with status, priority, and team filters."""
        async def override_get_current_user():
            return user_in_db

        app.dependency_overrides[get_current_user] = override_get_current_user

        filters = {
            "statuses": ["open", "done"],
            "priorities": ["high"],
            "team_id": 1
        }
        response = await test_client.post("/tasks/my", json=filters)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert isinstance(data, list)

        app.dependency_overrides.clear()

    async def test_get_my_tasks_unauthorized(self, test_client: AsyncClient):
        """Test that unauthorized user cannot get related tasks."""
        async def override_get_current_user():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await test_client.post("/tasks/my", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        app.dependency_overrides.clear()

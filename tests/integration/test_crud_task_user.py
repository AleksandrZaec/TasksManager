import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.schemas import TaskUserAdd, RoleUpdatePayload


@pytest.mark.asyncio
class TestTaskAssigneeCRUDAddExecutors:
    async def test_add_executors_success(
            self,
            test_session: AsyncSession,
            create_user, create_team,
            create_task,
            task_assignee_crud):
        """Add new executors to the task successfully."""
        creator = await create_user(email="creator@example.com")
        team = await create_team(name="Test Team", creator_id=creator.id)
        task = await create_task(team_id=team.id, creator_id=creator.id)

        user1 = await create_user(email="user1@example.com")
        user2 = await create_user(email="user2@example.com")

        users_to_add = [
            TaskUserAdd(user_id=user1.id, role="executor"),
            TaskUserAdd(user_id=user2.id, role="manager"),
        ]

        response = await task_assignee_crud.add_executors(test_session, task.id, users_to_add)

        added_user_ids = {user.id for user in response.added}
        assert user1.id in added_user_ids
        assert user2.id in added_user_ids
        assert len(response.errors) == 0

    async def test_add_executors_with_existing_and_missing_users(
            self, test_session: AsyncSession,
            create_user,
            create_team,
            create_task,
            task_assignee_crud):
        """Add executors including already assigned and non-existent users returns proper errors without exception."""
        creator = await create_user(email="creator2@example.com")
        team = await create_team(name="Test Team 2", creator_id=creator.id)
        task = await create_task(team_id=team.id, creator_id=creator.id)

        user1 = await create_user(email="user3@example.com")

        await task_assignee_crud.add_executors(test_session, task.id, [TaskUserAdd(user_id=user1.id, role="executor")])

        users_to_add = [
            TaskUserAdd(user_id=user1.id, role="executor"),
            TaskUserAdd(user_id=9999999, role="executor"),
        ]

        response = await task_assignee_crud.add_executors(test_session, task.id, users_to_add)

        errors_text = " ".join(response.errors)
        assert "already assigned" in errors_text
        assert "not found" in errors_text

        assert len(response.added) == 0

    async def test_add_executors_empty_list_raises(self, test_session: AsyncSession, task_assignee_crud):
        """Adding executors with empty list raises HTTP 400."""
        with pytest.raises(HTTPException) as exc_info:
            await task_assignee_crud.add_executors(test_session, 1, [])

        assert exc_info.value.status_code == 400
        assert "No users provided" in exc_info.value.detail


@pytest.mark.asyncio
class TestTaskAssigneeCRUDRemoveExecutors:
    async def test_remove_executors_success(
            self,
            test_session: AsyncSession,
            create_user, create_team,
            create_task,
            task_assignee_crud):
        """Remove executors from the task successfully."""
        creator = await create_user(email="creator4@example.com")
        team = await create_team(name="Remove Team", creator_id=creator.id)
        task = await create_task(team_id=team.id, creator_id=creator.id)

        user1 = await create_user(email="removeuser1@example.com")
        user2 = await create_user(email="removeuser2@example.com")

        await task_assignee_crud.add_executors(test_session, task.id, [
            TaskUserAdd(user_id=user1.id),
            TaskUserAdd(user_id=user2.id),
        ])

        response = await task_assignee_crud.remove_executors(test_session, task.id, [user1.id, user2.id, 9999999])

        assert set(response.removed) == {user1.id, user2.id}
        assert 9999999 in response.not_found

    async def test_remove_executors_empty_list_raises(self, test_session: AsyncSession, task_assignee_crud):
        """Removing executors with empty user_ids list raises HTTP 400."""
        with pytest.raises(HTTPException) as exc_info:
            await task_assignee_crud.remove_executors(test_session, 1, [])

        assert exc_info.value.status_code == 400
        assert "No user IDs provided" in exc_info.value.detail


@pytest.mark.asyncio
class TestTaskAssigneeCRUDUpdateRole:
    async def test_update_executor_role_success(
            self,
            test_session: AsyncSession,
            create_user, create_team,
            create_task,
            task_assignee_crud):
        """Update role of existing executor successfully."""
        creator = await create_user(email="creator5@example.com")
        team = await create_team(name="UpdateRole Team", creator_id=creator.id)
        task = await create_task(team_id=team.id, creator_id=creator.id)

        user = await create_user(email="roleuser@example.com")

        await task_assignee_crud.add_executors(test_session, task.id, [TaskUserAdd(user_id=user.id)])

        payload = RoleUpdatePayload(new_role="manager")

        response = await task_assignee_crud.update_executor_role(test_session, task.id, user.id, payload)

        assert response.msg == "Role updated"

    async def test_update_executor_role_not_found(self, test_session: AsyncSession, task_assignee_crud):
        """Update role fails with 404 if executor not found."""
        payload = RoleUpdatePayload(new_role="manager")

        with pytest.raises(HTTPException) as exc_info:
            await task_assignee_crud.update_executor_role(test_session, 999999, 999999, payload)

        assert exc_info.value.status_code == 404

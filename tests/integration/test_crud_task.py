import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.models import TaskPriority, TaskStatus, TaskAssigneeAssociation, TeamUserAssociation, TeamRole
from src.schemas import TaskCreate, TaskUpdate
from src.services.task import tasks_crud


@pytest.mark.asyncio
class TestTaskCRUDCreate:
    async def test_create_task_success(self, test_session: AsyncSession, create_user, create_team):
        """Create a task without assignees successfully."""
        creator = await create_user(email="creator_task@example.com")
        team = await create_team(name="TaskTeam", creator_id=creator.id)

        task_in = TaskCreate(
            title="Test Task",
            description="Task description",
            status=TaskStatus.OPEN,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            assignees=[],
        )

        task = await tasks_crud.create_task(test_session, task_in, creator_id=creator.id, team_id=team.id)

        assert task.title == "Test Task"
        assert hasattr(task, "id")

    async def test_create_task_with_assignees(self, test_session, create_user, create_team):
        """Create a task with valid assignees successfully."""
        creator = await create_user(email="creator2@example.com")
        team = await create_team(name="TaskTeam2", creator_id=creator.id)

        member1 = await create_user(email="member1@example.com")
        member2 = await create_user(email="member2@example.com")

        assoc1 = TeamUserAssociation(user_id=member1.id, team_id=team.id, role=TeamRole.EXECUTOR)
        assoc2 = TeamUserAssociation(user_id=member2.id, team_id=team.id, role=TeamRole.MANAGER)

        test_session.add_all([assoc1, assoc2])
        await test_session.commit()

        task_in = TaskCreate(
            title="Task With Assignees",
            description="Desc",
            status=TaskStatus.OPEN,
            priority=TaskPriority.HIGH,
            due_date=None,
            assignees=[
                {"user_id": member1.id, "role": "EXECUTOR"},
                {"user_id": member2.id, "role": "MANAGER"},
            ],
        )

        task = await tasks_crud.create_task(test_session, task_in, creator_id=creator.id, team_id=team.id)

        assert task.title == "Task With Assignees"

        stmt = select(TaskAssigneeAssociation).where(TaskAssigneeAssociation.task_id == task.id)
        result = await test_session.execute(stmt)
        associations = result.scalars().all()

        user_ids = {assoc.user_id for assoc in associations}
        assert member1.id in user_ids
        assert member2.id in user_ids

    async def test_create_task_with_invalid_assignee_raises(self, test_session: AsyncSession, create_user, create_team):
        """Raise 400 error if assignee user is invalid or not in team."""
        creator = await create_user(email="creator3@example.com")
        team = await create_team(name="TaskTeam3", creator_id=creator.id)

        invalid_user_id = 999999

        task_in = TaskCreate(
            title="Invalid Assignee Task",
            description="Desc",
            status=TaskStatus.OPEN,
            priority=TaskPriority.LOW,
            due_date=None,
            assignees=[
                {"user_id": invalid_user_id, "role": "EXECUTOR"},
            ],
        )

        with pytest.raises(HTTPException) as exc_info:
            await tasks_crud.create_task(test_session, task_in, creator_id=creator.id, team_id=team.id)

        assert exc_info.value.status_code == 400
        assert "Users not found or not in team" in exc_info.value.detail


@pytest.mark.asyncio
class TestTaskCRUDReadUpdate:
    async def test_get_task_by_id_success(self, test_session: AsyncSession, create_user, create_team, create_task):
        """Retrieve task by ID with creator email and assignees."""
        creator = await create_user(email="creator4@example.com")
        team = await create_team(name="TaskTeam4", creator_id=creator.id)

        task = await create_task(team_id=team.id, creator_id=creator.id)

        task_read = await tasks_crud.get_task_by_id(test_session, task.id)

        assert task_read.id == task.id
        assert task_read.creator_email == creator.email
        assert isinstance(task_read.assignees, list)

    async def test_update_task_success(self, test_session: AsyncSession, create_user, create_task):
        """Successfully update task title and description."""
        creator = await create_user(email="creator5@example.com")

        task = await create_task(creator_id=creator.id)

        update_data = TaskUpdate(title="Updated title", description="Updated desc")

        updated = await tasks_crud.update_task(test_session, task.id, update_data, creator_id=creator.id)

        assert updated.title == "Updated title"
        assert updated.description == "Updated desc"

    async def test_update_task_not_found(self, test_session: AsyncSession):
        """Raise 404 when updating a non-existent task."""
        update_data = TaskUpdate(title="Updated title")

        with pytest.raises(HTTPException) as exc_info:
            await tasks_crud.update_task(test_session, 999999, update_data, creator_id=1)

        assert exc_info.value.status_code == 404

    async def test_update_status_success(self, test_session: AsyncSession, create_user, create_task):
        """Successfully update task status."""
        creator = await create_user(email="creator6@example.com")
        task = await create_task(creator_id=creator.id)

        new_status = TaskStatus.IN_PROGRESS

        updated = await tasks_crud.update_status(test_session, task.id, new_status, changed_by_id=creator.id)

        assert updated.status == new_status


@pytest.mark.asyncio
class TestTaskCRUDQueries:
    async def test_get_user_related_tasks(self, test_session: AsyncSession, create_user, create_task):
        """Retrieve tasks related to a user."""
        creator = await create_user(email="creator7@example.com")
        task = await create_task(creator_id=creator.id)

        tasks = await tasks_crud.get_user_related_tasks(test_session, creator.id)

        assert any(t.id == task.id for t in tasks)

    async def test_get_team_tasks(self, test_session: AsyncSession, create_user, create_task, create_team):
        """Retrieve tasks for a specific team."""
        creator = await create_user(email="creator8@example.com")
        team = await create_team(name="TeamTasks", creator_id=creator.id)
        task = await create_task(team_id=team.id, creator_id=creator.id)

        tasks = await tasks_crud.get_team_tasks(test_session, team.id)

        assert any(t.id == task.id for t in tasks)

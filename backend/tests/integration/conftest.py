import pytest
from typing import List, Optional, Callable, Awaitable, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models import (
    TaskAssigneeAssociation, TeamRole, TaskStatus, TaskPriority, Task, Evaluation
)
from backend.src.services.meeting import MeetingCRUD
from backend.src.services.task_user import TaskAssigneeCRUD
from backend.src.services.team_user import TeamUserCRUD
from backend.src.services.user import UserCRUD
from backend.src.services.team import TeamCRUD
from backend.src.services.evaluation import EvaluationCRUD
from backend.src.schemas import UserCreate, TeamCreate, TeamUserAdd


@pytest.fixture(scope="session")
def users_crud() -> UserCRUD:
    """Provide UserCRUD instance."""
    return UserCRUD()


@pytest.fixture(scope="session")
def teams_crud() -> TeamCRUD:
    """Provide TeamCRUD instance."""
    return TeamCRUD()


@pytest.fixture
def team_users_crud() -> TeamUserCRUD:
    """Provide TeamUserCRUD instance."""
    return TeamUserCRUD()


@pytest.fixture
def task_assignee_crud() -> TaskAssigneeCRUD:
    """Provide TaskAssigneeCRUD instance."""
    return TaskAssigneeCRUD()


@pytest.fixture
def meetings_crud() -> MeetingCRUD:
    """Provide MeetingCRUD instance."""
    return MeetingCRUD()


@pytest.fixture
def evaluation_crud() -> EvaluationCRUD:
    """Provide EvaluationCRUD instance."""
    return EvaluationCRUD()


@pytest.fixture
async def create_user(
        test_session: AsyncSession,
        users_crud: UserCRUD
) -> Callable[[str, str, str, str], Awaitable]:
    """Factory fixture to create a user with default or given data."""

    async def _create_user(
            email: str = "user@example.com",
            password: str = "Password123!",
            first_name: str = "First",
            last_name: str = "Last"
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
async def create_team(
        test_session: AsyncSession,
        teams_crud: TeamCRUD,
        create_user: Callable[..., Awaitable]
) -> Callable[[str, str, Optional[int], Optional[List[TeamUserAdd]]], Awaitable]:
    """Factory fixture to create a team with optional creator and users."""

    async def _create_team(
            name: str = "Test Team",
            description: str = "Description",
            creator_id: Optional[int] = None,
            users: Optional[List[TeamUserAdd]] = None
    ):
        if creator_id is None:
            creator = await create_user()
            creator_id = creator.id
        users = users or []
        team_in = TeamCreate(name=name, description=description, users=users)
        team = await teams_crud.create_team(test_session, team_in, creator_id=creator_id)
        return team

    return _create_team


@pytest.fixture
async def create_task(
        test_session: AsyncSession,
        create_user: Callable[..., Awaitable],
        create_team: Callable[..., Awaitable]
) -> Callable[..., Awaitable]:
    """Factory fixture to create a Task with optional assignees, creator, and team."""

    async def _create_task(
            *,
            title: str = "Test task",
            description: str = "Task desc",
            status: TaskStatus = TaskStatus.OPEN,
            priority: TaskPriority = TaskPriority.MEDIUM,
            due_date: Optional = None,
            assignees: Optional[List[TaskAssigneeAssociation]] = None,
            creator_id: Optional[int] = None,
            team_id: Optional[int] = None
    ) -> Task:
        creator_id = creator_id or (await create_user()).id
        team_id = team_id or (await create_team(creator_id=creator_id)).id
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            creator_id=creator_id,
            team_id=team_id
        )
        test_session.add(task)
        await test_session.flush()
        if assignees:
            for assignee in assignees:
                assoc = TaskAssigneeAssociation(
                    task_id=task.id,
                    user_id=assignee.user_id,
                    role=assignee.role or "EXECUTOR"
                )
                test_session.add(assoc)
            await test_session.flush()
        await test_session.commit()
        await test_session.refresh(task)
        return task

    return _create_task


@pytest.fixture
async def create_team_with_users(
        test_session: AsyncSession,
        create_user: Callable[..., Awaitable],
        teams_crud: TeamCRUD
) -> Callable[[str, str, Optional[List[str]]], Awaitable[Tuple]]:
    """Factory fixture to create a Team with a creator and optional users."""

    async def _create_team(
            name: str = "Test Team",
            creator_email: str = "creator@example.com",
            user_emails: Optional[List[str]] = None
    ) -> Tuple:
        creator = await create_user(email=creator_email)
        users = []
        if user_emails:
            for email in user_emails:
                user = await create_user(email=email)
                users.append(user)
        team_in = TeamCreate(
            name=name,
            description="Description",
            users=[TeamUserAdd(user_id=user.id, role=TeamRole.EXECUTOR.value) for user in users]
        )
        team = await teams_crud.create_team(test_session, team_in, creator_id=creator.id)
        return team, creator, users

    return _create_team


@pytest.fixture
async def create_task_assignees(
        test_session: AsyncSession,
        create_user: Callable[..., Awaitable]
) -> Callable[..., Awaitable]:
    """Factory to add assignees to a task."""

    async def _create_task_assignees(task_id: int, count: int = 1):
        users = []
        for i in range(count):
            user = await create_user(email=f"assignee{i}@example.com")
            assoc = TaskAssigneeAssociation(
                task_id=task_id,
                user_id=user.id,
                role="EXECUTOR"
            )
            test_session.add(assoc)
            users.append(user)
        await test_session.flush()
        await test_session.commit()
        return users

    return _create_task_assignees


@pytest.fixture
async def create_evaluation(
        test_session: AsyncSession,
        create_task_assignees: Callable[..., Awaitable]
) -> Callable[..., Awaitable]:
    """Factory to create evaluation with default score and feedback."""

    async def _create_evaluation(
            task_id: int,
            evaluator_id: int,
            score: int = 5,
            feedback: str = "Good work"
    ):
        evaluation = Evaluation(
            task_id=task_id,
            evaluator_id=evaluator_id,
            score=score,
            feedback=feedback,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(evaluation)
        await test_session.flush()
        await test_session.commit()
        await test_session.refresh(evaluation)
        return evaluation

    return _create_evaluation

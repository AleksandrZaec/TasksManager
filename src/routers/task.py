from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.deps.permissions import admin_manager_in_team, block_everyone, can_change_status, is_team_member
from src.models import TaskStatus, TaskPriority, User
from src.services.auth import get_current_user
from src.services.task import tasks_crud
from src.schemas import TaskCreate, TaskUpdate, TaskRead, TaskShortRead, TaskStatusUpdate, TaskFilter, \
    UserPayload
from src.config.db import get_db

router = APIRouter()


@router.post(
    "/{team_id}/tasks/",
    response_model=TaskShortRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task for a team",
    description="Create a new task assigned to the specified team. Only admins or managers in the team can create tasks."
)
async def create_task(
    team_id: int = Path(..., description="ID of the team to assign the task to"),
    task_in: TaskCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: UserPayload = Depends(admin_manager_in_team)
) -> TaskShortRead:
    """Create a new task for a specific team."""
    return await tasks_crud.create_task(db, task_in, current_user.id, team_id)


@router.get(
    "/",
    response_model=List[TaskShortRead],
    summary="Get all tasks",
    description="Retrieve a list of all tasks in the system. This endpoint is disabled."
)
async def get_all_tasks(
        db: AsyncSession = Depends(get_db),
        _=Depends(block_everyone)
) -> List[TaskShortRead]:
    """Get all tasks."""
    return await tasks_crud.get_all_task(db)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task by ID",
    description="Retrieve detailed information about a task by its ID. Any authenticated user can access."
)
async def get_task_by_id(
        task_id: int = Path(..., description="ID of the task to retrieve"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> TaskRead:
    """Get a task by its ID with detailed info."""
    return await tasks_crud.get_task_by_id(db, task_id)


@router.put(
    "/{team_id}/{task_id}",
    response_model=TaskShortRead,
    summary="Update a task",
    description="Update the details of a task by its ID within the specified team. Only admins or managers in the team can update tasks."
)
async def update_task(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task to update"),
        task_in: TaskUpdate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_manager_in_team)
) -> TaskShortRead:
    """Update an existing task."""
    return await tasks_crud.update_task(db, task_id, task_in, current_user.id)


@router.delete(
    "/{team_id}/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by ID within the specified team. Only admins or managers in the team can delete tasks."
)
async def delete_task(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task to delete"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_manager_in_team)
) -> None:
    """Delete a task by ID."""
    await tasks_crud.delete(db, task_id)
    return None


@router.patch(
    "/{team_id}/{task_id}/status",
    response_model=TaskShortRead,
    summary="Update task status",
    description="Update the status of a task and log the status change. Allowed for admins, managers of the team, or task assignees."
)
async def update_task_status(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        status_update: TaskStatusUpdate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(can_change_status)
) -> TaskShortRead:
    """Update status of a task and log the change."""
    return await tasks_crud.update_status(db, task_id, status_update.status, current_user.id)


@router.post(
    "/my",
    response_model=List[TaskShortRead],
    status_code=status.HTTP_201_CREATED,
    summary="Get tasks related to current user",
    description="Get tasks where the current user is an author or an executor, with optional filtering by status, priority, and team."
)
async def get_my_tasks(
        filters: TaskFilter = ...,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[TaskShortRead]:
    """Get tasks where the current user is the author or performer."""
    return await tasks_crud.get_user_related_tasks(db, current_user.id, filters.statuses, filters.priorities,
                                                   filters.team_id)


@router.get(
    "/{team_id}/tasks",
    response_model=List[TaskShortRead],
    summary="Get tasks for a team",
    description="Retrieve tasks for the specified team, optionally filtered by statuses and priorities. Only team members can access."
)
async def get_tasks_for_team(
        team_id: int = Path(..., description="ID of the team"),
        statuses: Optional[List[TaskStatus]] = Query(None, description="Filter by task statuses"),
        priorities: Optional[List[TaskPriority]] = Query(None, description="Filter by task priorities"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_team_member)
) -> List[TaskShortRead]:
    """Retrieve all tasks for a specific team."""
    return await tasks_crud.get_team_tasks(db, team_id, statuses, priorities)

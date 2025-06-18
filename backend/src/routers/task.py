from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend.src.models import TaskStatus, TaskPriority, User
from backend.src.services.auth import get_current_user
from backend.src.services.task import tasks_crud
from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskShortRead, TaskStatusUpdate, TaskFilter
from backend.src.config.db import get_db

router = APIRouter()


@router.post("/teams/{team_id}/tasks/", response_model=TaskShortRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    team_id: int,
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskShortRead:
    """Create a new task for a specific team."""
    return await tasks_crud.create_task(db, task_in, current_user.id, team_id)


@router.get("/", response_model=List[TaskShortRead])
async def get_all_tasks(
        db: AsyncSession = Depends(get_db)
) -> List[TaskShortRead]:
    """Get all tasks."""
    return await tasks_crud.get_all_task(db)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_by_id(
        task_id: int,
        db: AsyncSession = Depends(get_db)
) -> TaskRead:
    """Get a task by its ID with detailed info."""
    return await tasks_crud.get_task_by_id(db, task_id)


@router.put("/{task_id}", response_model=TaskShortRead)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> TaskShortRead:
    """Update an existing task."""
    return await tasks_crud.update_task(db, task_id, task_in, current_user.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task by ID."""
    await tasks_crud.delete(db, task_id)
    return None


@router.patch("/{task_id}/status", response_model=TaskShortRead)
async def update_task_status(
        task_id: int,
        status_update: TaskStatusUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> TaskShortRead:
    """Update status of a task and log the change."""
    return await tasks_crud.update_status(db, task_id, status_update.status, current_user.id)


@router.post("/my", response_model=List[TaskShortRead], status_code=status.HTTP_201_CREATED)
async def get_my_tasks(
        filters: TaskFilter,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[TaskShortRead]:
    """Get tasks where the current user is the author or performer."""
    return await tasks_crud.get_user_related_tasks(db, current_user.id, filters.statuses, filters.priorities,
                                                   filters.team_id)


@router.get("/teams/{team_id}/tasks", response_model=List[TaskShortRead])
async def get_tasks_for_team(
        team_id: int,
        statuses: Optional[List[TaskStatus]] = Query(None),
        priorities: Optional[List[TaskPriority]] = Query(None),
        db: AsyncSession = Depends(get_db)
) -> List[TaskShortRead]:
    """Retrieve all tasks for a specific team."""
    return await tasks_crud.get_team_tasks(db, team_id, statuses, priorities)

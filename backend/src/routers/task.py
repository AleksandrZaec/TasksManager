from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from backend.src.models import TaskStatus, TaskPriority, user, User
from backend.src.schemas.task_user import TaskAssigneeCreate
from backend.src.services.auth import get_current_user
from backend.src.services.task import tasks_crud
from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskShortRead, TaskStatusUpdate, TaskFilter
from backend.src.config.db import get_db
from backend.src.services.task_user import task_user_crud

router = APIRouter()


@router.post("/", response_model=TaskShortRead, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> TaskShortRead:
    print("USER IN CREATE TASK:", current_user)
    """Create a new task."""
    return await tasks_crud.create_task(
        db=db,
        task_in=task_in,
        creator_id=current_user.id,
        team_id=task_in.team_id
    )


@router.get("/", response_model=List[TaskShortRead])
async def get_all_tasks(
        db: AsyncSession = Depends(get_db)
) -> List[TaskShortRead]:
    """Get all tasks."""
    return await tasks_crud.get_all(db=db)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_by_id(
        task_id: int,
        db: AsyncSession = Depends(get_db)
) -> TaskRead:
    """Get a task by its ID with detailed info."""
    return await tasks_crud.get_by_id(db=db, task_id=task_id)


@router.put("/{task_id}", response_model=TaskShortRead)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db)
) -> TaskShortRead:
    """Update an existing task."""
    return await tasks_crud.update(db=db, obj_id=task_id, obj_in=task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a task by ID."""
    await tasks_crud.delete(db=db, obj_id=task_id)
    return None


@router.patch("/{task_id}/status", response_model=TaskShortRead)
async def update_task_status(
        task_id: int,
        status_update: TaskStatusUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> TaskShortRead:
    """Update status of a task and log the change."""
    return await tasks_crud.update_status(
        db=db,
        task_id=task_id,
        new_status=status_update.status,
        changed_by_id=current_user.id
    )


@router.post("/my", response_model=List[TaskShortRead], status_code=status.HTTP_201_CREATED)
async def get_my_tasks(
        filters: TaskFilter,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[TaskShortRead]:
    """Get tasks where the current user is the author or performer."""
    return await tasks_crud.get_user_related_tasks(
        db=db,
        user_id=current_user.id,
        statuses=filters.statuses,
        priorities=filters.priorities,
        team_id=filters.team_id
    )


@router.get("/teams/{team_id}/tasks", response_model=List[TaskShortRead])
async def get_tasks_for_team(
        team_id: int,
        statuses: Optional[List[TaskStatus]] = Query(None),
        priorities: Optional[List[TaskPriority]] = Query(None),
        db: AsyncSession = Depends(get_db)
) -> List[TaskShortRead]:
    """Retrieve all tasks for a specific team."""
    return await tasks_crud.get_team_tasks(
        db=db,
        team_id=team_id,
        statuses=statuses,
        priorities=priorities
    )


@router.post("/{task_id}/assignees", status_code=status.HTTP_201_CREATED)
async def add_executor_to_task(
        task_id: int,
        obj_in: TaskAssigneeCreate,
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    obj = TaskAssigneeCreate(task_id=task_id, user_id=obj_in.user_id, role=obj_in.role)
    return await task_user_crud.add_executor(db, task_id, obj_in)


@router.delete("/{task_id}/assignees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_executor_from_task(task_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Remove an executor from a task."""
    await task_user_crud.remove_executor(db, task_id, user_id)


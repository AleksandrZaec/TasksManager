from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.src.services.auth import get_current_user
from backend.src.services.task import tasks_crud
from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskShortRead, TaskStatusUpdate
from backend.src.config.db import get_db
from backend.src.models.user import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskShortRead, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> TaskShortRead:
    """Create a new task."""
    return await tasks_crud.create(
        db=db,
        task_in=task_in,
        creator_id=current_user.id,
        team_id=task_in.team_id
    )


@router.get("/", response_model=List[TaskShortRead])
async def get_all_tasks(
        db: AsyncSession = Depends(get_db),
) -> List[TaskShortRead]:
    """Get all tasks."""
    return await tasks_crud.get_all(db=db)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_by_id(
        task_id: int,
        db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Get a task by its ID with detailed info."""
    return await tasks_crud.get_by_id(db=db, task_id=task_id)


@router.put("/{task_id}", response_model=TaskShortRead)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
) -> TaskShortRead:
    """Update an existing task."""
    task = await tasks_crud.update(db=db, obj_id=task_id, obj_in=task_in)
    return task


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
        current_user: User = Depends(get_current_user),
) -> TaskShortRead:
    """Update status of a task and log the change."""
    return await tasks_crud.update_status(
        db=db,
        task_id=task_id,
        new_status=status_update.status,
        changed_by_id=current_user.id
    )

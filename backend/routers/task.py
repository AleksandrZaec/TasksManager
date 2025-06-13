from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.schemas.task import TaskCreate, TaskRead, TaskUpdate
from backend.crud.task import task_crud
from backend.config.db import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=List[TaskRead])
async def read_tasks(db: AsyncSession = Depends(get_db)) -> List[TaskRead]:
    """Get all tasks."""
    tasks = await task_crud.get_all(db)
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)) -> TaskRead:
    """Get a task by its ID."""
    task = await task_crud.get_by_id(db, task_id)
    return task


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)) -> TaskRead:
    """Create a new task."""
    create_task = await task_crud.create(
        db=db,
        obj_in=task_in,
        # creator_id=current_user.user_id,
        team_id=task_in.team_id
    )
    return create_task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)) -> TaskRead:
    """Update a task by its ID."""
    update_task = await task_crud.update(db, obj_id=task_id, obj_in=task_in)
    return update_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a task by its ID."""
    await task_crud.delete(db, task_id)
    return None

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from backend.src.schemas.task_user import TaskAssigneeCreate, RoleUpdatePayload
from backend.src.config.db import get_db
from backend.src.schemas.team_user import AddUsersResponse
from backend.src.services.task_user import task_user_crud

router = APIRouter()


@router.post("/{task_id}/assignees", response_model=AddUsersResponse, status_code=status.HTTP_201_CREATED)
async def add_executor_to_task(
        task_id: int,
        obj_in: TaskAssigneeCreate,
        db: AsyncSession = Depends(get_db)
) -> AddUsersResponse:
    """Add a user as an executor to the specified task."""
    return await task_user_crud.add_executors(db, task_id, obj_in.users)


@router.delete("/{task_id}/assignees/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_executor_from_task(task_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Remove an executor from a task."""
    await task_user_crud.remove_executor(db, task_id, user_id)


@router.patch("/{task_id}/assignees/{user_id}/role", status_code=status.HTTP_200_OK)
async def update_executor_role(
        task_id: int,
        user_id: int,
        role_update: RoleUpdatePayload,
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Update the role of an executor in the specified task."""
    return await task_user_crud.update_executor_role(db, task_id, user_id, role_update.new_role)

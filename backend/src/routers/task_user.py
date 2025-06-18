from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.schemas.task_user import TaskAssigneeCreate, RoleUpdatePayload, AddUsersResponse, UsersRemoveResponse, \
    UsersRemoveRequest, RoleUpdateResponse
from backend.src.config.db import get_db
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


@router.delete("/{task_id}/assignees", response_model=UsersRemoveResponse, status_code=status.HTTP_200_OK)
async def remove_executors_from_task(
        task_id: int,
        obj_in: UsersRemoveRequest,
        db: AsyncSession = Depends(get_db)
) -> UsersRemoveResponse:
    """Remove multiple executors from a task by their user IDs."""
    return await task_user_crud.remove_executors(db, task_id, obj_in.user_ids)


@router.patch("/{task_id}/assignees/{user_id}/role", response_model=RoleUpdateResponse, status_code=status.HTTP_200_OK)
async def update_executor_role(
        task_id: int,
        user_id: int,
        role_update: RoleUpdatePayload,
        db: AsyncSession = Depends(get_db)
) -> RoleUpdateResponse:
    """Update the role of an executor in the specified task."""
    return await task_user_crud.update_executor_role(db, task_id, user_id, role_update.new_role)

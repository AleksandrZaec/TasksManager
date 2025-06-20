from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.deps.permissions import admin_manager_in_team
from backend.src.schemas import TaskAssigneeCreate, RoleUpdatePayload, AddUsersResponse, UsersRemoveResponse, \
    UsersRemoveRequest, RoleUpdateResponse, UserPayload
from backend.src.config.db import get_db
from backend.src.services.task_user import task_user_crud

router = APIRouter()


@router.post(
    "/{team_id}/{task_id}/assignees",
    response_model=AddUsersResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add executors to a task",
    description="Add one or more users as executors to the specified task. Only admins or managers of the team can perform this action."
)
async def add_executor_to_task(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        obj_in: TaskAssigneeCreate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_manager_in_team)
) -> AddUsersResponse:
    """Add a user as an executor to the specified task."""
    return await task_user_crud.add_executors(db, task_id, obj_in.users)


@router.delete(
    "/{team_id}/{task_id}/assignees",
    response_model=UsersRemoveResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove executors from a task",
    description="Remove multiple executors from the specified task by their user IDs. Only admins or managers of the team can perform this action."
)
async def remove_executors_from_task(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        obj_in: UsersRemoveRequest = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_manager_in_team)
) -> UsersRemoveResponse:
    """Remove multiple executors from a task by their user IDs."""
    return await task_user_crud.remove_executors(db, task_id, obj_in.user_ids)


@router.patch(
    "/{team_id}/{task_id}/{user_id}/role",
    response_model=RoleUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update executor role in task",
    description="Update the role of a specific executor in the given task. Only admins or managers of the team can perform this action."
)
async def update_executor_role(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        user_id: int = Path(..., description="ID of the executor user"),
        role_update: RoleUpdatePayload = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_manager_in_team)
) -> RoleUpdateResponse:
    """Update the role of an executor in the specified task."""
    return await task_user_crud.update_executor_role(db, task_id, user_id, role_update.new_role)

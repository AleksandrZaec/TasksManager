from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from src.config.db import get_db
from src.deps.permissions import is_admin_and_member
from src.schemas import AddUsersResponse, TeamUsersCreate, UsersRemoveResponse, UsersRemoveRequest, \
    TeamUserUpdateRole, UserPayload
from src.services.team_user import team_users_crud

router = APIRouter()


@router.post(
    "/{team_id}/users",
    response_model=AddUsersResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add users to a team",
    description="Add one or more users to the specified team with their assigned roles. Access restricted to admins who are members of the team."
)
async def add_user_to_team(
        team_id: int = Path(..., description="ID of the team to add users to"),
        user_data: TeamUsersCreate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin_and_member)
) -> AddUsersResponse:
    """Add a users to a team with a specified role."""
    return await team_users_crud.add_users(db, team_id, user_data.users)


@router.delete(
    "/{team_id}/users",
    response_model=UsersRemoveResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove multiple users from a team",
    description="Remove several users from the specified team by their IDs. Access restricted to admins who are members of the team."
)
async def remove_users_bulk_from_team(
        team_id: int = Path(..., description="ID of the team to remove users from"),
        obj_in: UsersRemoveRequest = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin_and_member)
) -> UsersRemoveResponse:
    """Remove multiple users from a team."""
    return await team_users_crud.remove_users(db, team_id, obj_in.user_ids)


@router.patch(
    "/{team_id}/users/{user_id}/role",
    summary="Update user's role in a team",
    description="Update the role of a specific user in the specified team. Access restricted to admins who are members of the team."
)
async def update_user_role_in_team(
        team_id: int = Path(..., description="ID of the team"),
        user_id: int = Path(..., description="ID of the user whose role will be updated"),
        role_data: TeamUserUpdateRole = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin_and_member)
) -> Dict[str, str]:
    """Update a user's role in a team."""
    return await team_users_crud.update_user_role(db, team_id, user_id, role_data.role)

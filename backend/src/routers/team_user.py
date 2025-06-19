from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from typing import Dict
from backend.src.schemas import AddUsersResponse, TeamUsersCreate, UsersRemoveResponse, UsersRemoveRequest, \
    TeamUserUpdateRole
from backend.src.services.team_user import team_users_crud

router = APIRouter()


@router.post("/{team_id}/users", response_model=AddUsersResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_team(
        team_id: int,
        user_data: TeamUsersCreate,
        db: AsyncSession = Depends(get_db)
) -> AddUsersResponse:
    """Add a users to a team with a specified role."""
    return await team_users_crud.add_users(db, team_id, user_data.users)


@router.delete("/{team_id}/users", response_model=UsersRemoveResponse, status_code=status.HTTP_200_OK)
async def remove_users_bulk_from_team(
        team_id: int,
        obj_in: UsersRemoveRequest,
        db: AsyncSession = Depends(get_db)
) -> UsersRemoveResponse:
    """Remove multiple users from a team."""
    return await team_users_crud.remove_users(db, team_id, obj_in.user_ids)


@router.patch("/{team_id}/users/{user_id}/role")
async def update_user_role_in_team(
        team_id: int,
        user_id: int,
        role_data: TeamUserUpdateRole,
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Update a user's role in a team."""
    return await team_users_crud.update_user_role(db, team_id, user_id, role_data.role)

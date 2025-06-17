from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.schemas.team_user import AddUsersResponse
from backend.src.schemas.team_user import TeamUserUpdateRole, TeamUsersCreate
from typing import Dict, List

from backend.src.schemas.user import UserRead
from backend.src.services.team_user import team_users_crud

router = APIRouter()


@router.post("/{team_id}/users",  response_model=AddUsersResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_team(
    team_id: int,
    user_data: TeamUsersCreate,
    db: AsyncSession = Depends(get_db)
) -> AddUsersResponse:
    """Add a users to a team with a specified role."""
    return await team_users_crud.add_users_bulk(db, team_id, user_data.users)


@router.delete("/{team_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_team(team_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Remove a single user from a team."""
    await team_users_crud.remove_user(db, team_id, user_id)


@router.patch("/{team_id}/users/{user_id}/role")
async def update_user_role_in_team(
        team_id: int,
        user_id: int,
        role_data: TeamUserUpdateRole,
        db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Update a user's role in a team."""
    return await team_users_crud.update_user_role(db, team_id, user_id, role_data.role)


@router.get("/teams/{team_id}/users", response_model=List[UserRead])
async def get_team_users(team_id: int, db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    """Get all users who are members of the team."""
    return await team_users_crud.get_team_users(db, team_id)

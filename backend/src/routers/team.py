from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.schemas.team import TeamCreate, TeamUpdate, TeamRead, TeamWithUsersAndTask
from backend.src.schemas.team_user import TeamUserAdd, TeamUserUpdateRole
from backend.src.services.team import team_crud
from typing import List, Dict
from backend.src.services.team_user import team_users_crud

router = APIRouter()


@router.post("/", response_model=TeamRead, status_code=201)
async def create_team(team_in: TeamCreate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Create a new team."""
    return await team_crud.create(db, team_in)


@router.get("/{team_id}", response_model=TeamWithUsersAndTask)
async def read_team(team_id: int, db: AsyncSession = Depends(get_db)) -> TeamWithUsersAndTask:
    """Get team details by ID with users and tasks."""
    return await team_crud.get_by_id_with_relations(db, team_id)


@router.get("/", response_model=List[TeamRead])
async def read_teams(db: AsyncSession = Depends(get_db)) -> List[TeamRead]:
    """List teams with pagination."""
    return await team_crud.get_all(db)


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, team_in: TeamUpdate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Update a team by ID."""
    return await team_crud.update(db, team_id, team_in)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a team by ID."""
    await team_crud.delete(db, team_id)
    return None


@router.post("/{team_id}/users")
async def add_user_to_team(team_id: int, user_data: TeamUserAdd, db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """Add a user to a team with a specified role."""
    return await team_users_crud.add_user(db, team_id, user_data.email, user_data.role)


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



from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.schemas.team import TeamCreate, TeamUpdate, TeamRead, TeamWithUsersAndTask
from backend.src.services.team import teams_crud
from typing import List


router = APIRouter()


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(team_in: TeamCreate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Create a new team."""
    return await teams_crud.create_team(db, team_in)


@router.get("/{team_id}", response_model=TeamWithUsersAndTask)
async def read_team(team_id: int, db: AsyncSession = Depends(get_db)) -> TeamWithUsersAndTask:
    """Get team details by ID with users and tasks."""
    return await teams_crud.get_by_id_with_relations(db, team_id)


@router.get("/", response_model=List[TeamRead])
async def read_teams_all(db: AsyncSession = Depends(get_db)) -> List[TeamRead]:
    """List teams."""
    return await teams_crud.get_all(db)


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, team_in: TeamUpdate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Update a team by ID."""
    return await teams_crud.update_team(db, team_id, team_in)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a team by ID."""
    await teams_crud.delete(db, team_id)
    return None




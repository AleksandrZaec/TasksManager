from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.schemas.team import TeamCreate, TeamUpdate, TeamRead, TeamWithUsersAndTask
from backend.src.services.team import team_crud
from typing import List

router = APIRouter()


@router.post("/", response_model=TeamRead, status_code=201)
async def create_team(team_in: TeamCreate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Create a new team."""
    team = await team_crud.create(db, team_in)
    return team


@router.get("/{team_id}", response_model=TeamWithUsersAndTask)
async def read_team(team_id: int, db: AsyncSession = Depends(get_db)) -> TeamWithUsersAndTask:
    """Get team details by ID with users and tasks."""
    team = await team_crud.get_by_id_with_relations(db, team_id)
    return team


@router.get("/", response_model=List[TeamRead])
async def read_teams(db: AsyncSession = Depends(get_db)) -> List[TeamRead]:
    """List teams with pagination."""
    teams = await team_crud.get_all(db)
    return teams


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, team_in: TeamUpdate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Update a team by ID."""
    team = await team_crud.update(db, team_id, team_in)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a team by ID."""
    await team_crud.delete(db, team_id)
    return None

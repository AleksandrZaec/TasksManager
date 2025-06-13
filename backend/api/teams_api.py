from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config.db import get_db
from backend.schemas.TeamUserAssociation_schemas import TeamUserAssociationRead, TeamUserAssociationCreate, \
    TeamUserAssociationUpdate
from backend.schemas.teams_schemas import TeamCreate, TeamRead, TeamUpdate
from backend.crud.teams_crud import team_crud, team_user_association_crud
from typing import List

router = APIRouter()


@router.get("/", response_model=List[TeamRead])
async def read_teams(db: AsyncSession = Depends(get_db)) -> List[TeamRead]:
    """Get a list of all teams."""
    teams = await team_crud.get_all(db)
    return teams


@router.post("/", response_model=TeamRead)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Create a new team."""
    created_team = await team_crud.create(db, team)
    return created_team


@router.get("/{team_id}", response_model=TeamRead)
async def read_team(team_id: int, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Get a team by ID."""
    team = await team_crud.get_by_id(db, team_id)
    return team


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, data: TeamUpdate, db: AsyncSession = Depends(get_db)) -> TeamRead:
    """Update a team by ID."""
    updated_team = await team_crud.update(db, team_id, data)
    return updated_team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a team by ID."""
    await team_crud.delete(db, team_id)
    return None


@router.post("/{team_id}/members", response_model=TeamUserAssociationRead, status_code=status.HTTP_201_CREATED)
async def add_user_to_team(
    team_id: int,
    member_in: TeamUserAssociationCreate,
    db: AsyncSession = Depends(get_db)
) -> TeamUserAssociationRead:
    """Add a user to a specific team with a role."""
    new_member = await team_user_association_crud.add_user_to_team(
        db=db,
        team_id=team_id,
        user_id=member_in.user_id,
        role=member_in.role
    )
    return new_member


@router.delete("/{team_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_team(
        team_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db)
) -> None:
    """Remove a user from a team."""
    await team_user_association_crud.remove_user(db, team_id, user_id)
    return None


@router.put("/{team_id}/{user_id}", response_model=TeamUserAssociationRead)
async def update_user_role(team_id: int,
                           user_id: int,
                           association_in: TeamUserAssociationUpdate,
                           db: AsyncSession = Depends(get_db)
                           ) -> TeamUserAssociationRead:
    """Update a user's role in a team."""
    if association_in.role is None:
        raise HTTPException(status_code=400, detail="Role is required")

    return await team_user_association_crud.update_role(db, team_id, user_id, association_in.role)

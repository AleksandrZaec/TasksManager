from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.src.config.db import get_db
from backend.src.deps.permissions import is_admin, is_team_member, is_admin_and_member
from backend.src.models import User
from backend.src.schemas import TeamCreate, TeamUpdate, TeamRead, TeamWithUsersAndTask, UserPayload
from backend.src.services.auth import get_current_user
from backend.src.services.team import teams_crud

router = APIRouter()


@router.post(
    "/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    description="Create a new team. Only admins can perform this action."
)
async def create_team(
        team_in: TeamCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin)
) -> TeamRead:
    """Create a new team."""
    return await teams_crud.create_team(db, team_in, current_user.id)


@router.get(
    "/my_teams",
    response_model=List[TeamRead],
    summary="Get teams of current user",
    description="Retrieve a list of teams where the current user is a member."
)
async def get_my_teams(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> List[TeamRead]:
    return await teams_crud.get_user_teams(db, current_user.id)


@router.get(
    "/{team_id}",
    response_model=TeamWithUsersAndTask,
    summary="Get team details",
    description="Get detailed information about a team by ID including its users and tasks. Accessible by team members only."
)
async def read_team(
        team_id: int = Path(..., description="ID of the team to retrieve"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_team_member)
) -> TeamWithUsersAndTask:
    """Get team details by ID with users and tasks."""
    return await teams_crud.get_by_id_with_relations(db, team_id)


@router.get(
    "/",
    response_model=List[TeamRead],
    summary="List all teams",
    description="Retrieve a list of all teams. Only admins can access this endpoint."
)
async def read_teams_all(
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin)
) -> List[TeamRead]:
    """List teams."""
    return await teams_crud.get_all(db)


@router.put(
    "/{team_id}",
    response_model=TeamRead,
    summary="Update team",
    description="Update the information of a team by its ID. Accessible by admins who are members of the team."
)
async def update_team(
        team_id: int = Path(..., description="ID of the team to update"),
        team_in: TeamUpdate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin_and_member)
) -> TeamRead:
    """Update a team by ID."""
    return await teams_crud.update_team(db, team_id, team_in)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="Delete a team by ID. Accessible by admins who are members of the team."
)
async def delete_team(
        team_id: int = Path(..., description="ID of the team to delete"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin_and_member)
) -> None:
    """Delete a team by ID."""
    await teams_crud.delete(db, team_id)
    return None
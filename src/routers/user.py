from fastapi import APIRouter, Depends, status, Path
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.deps.permissions import is_admin, block_everyone, is_team_member
from src.services.auth import get_current_user
from src.services.user import users_crud
from src.models import UserRole
from src.schemas import UserCreate, UserRead, UserUpdate, UserReadWithTeams, UserPayload

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserRead],
    summary="Get all users",
    description="Retrieve a list of all users in the system."
)
async def read_users(
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin)
) -> List[UserRead]:
    """Get a list of all users."""
    return await users_crud.get_all(db)


@router.get(
    "/me",
    response_model=UserReadWithTeams,
    summary="Get own profile",
    description="Retrieve the profile and team membership information of the currently authenticated user."
)
async def read_own_user_detail(
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(get_current_user),
) -> UserReadWithTeams:
    """Get current user's profile."""
    return await users_crud.get_with_teams(db, current_user.id)


@router.put(
    "/me",
    response_model=UserRead,
    summary="Update own profile",
    description="Update the profile of the currently authenticated user."
)
async def update_user(
        user_in: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(get_current_user),
) -> UserRead:
    """Update current user's profile."""
    return await users_crud.update(db, current_user.id, user_in)


@router.get(
    "/{user_id}",
    response_model=UserReadWithTeams,
    summary="Get user by ID (admin only)",
    description="Retrieve detailed information about a user by their ID. Requires ADMIN role."
)
async def read_user_detail(
        user_id: int = Path(..., description="ID of the user to retrieve"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin)
) -> UserRead:
    """Get a user by ID."""
    return await users_crud.get_with_teams(db, user_id)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user in the system with the provided details."
)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
) -> UserRead:
    """Create a new user."""
    return await users_crud.create(db, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (disabled)",
    description="Delete a user by ID. **Currently disabled for all users.**"
)
async def delete_user(
        user_id: int = Path(..., description="ID of the user to delete"),
        db: AsyncSession = Depends(get_db),
        _=Depends(block_everyone)
) -> None:
    """Delete a user by ID."""
    await users_crud.delete(db, user_id)
    return None


@router.put(
    "/{user_id}/set_role",
    response_model=UserRead,
    summary="Set user global role (admin only)",
    description="Set the global role for a user. Access restricted to ADMIN users."
)
async def set_user_role(
        user_id: int = Path(..., description="ID of the user to update role"),
        role: UserRole = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_admin)
) -> UserRead:
    """Set global role for a user (admin only)."""
    return await users_crud.set_global_role(db, user_id, role)


@router.get(
    "/teams/{team_id}/users",
    response_model=List[UserRead],
    summary="Get team members",
    description="Retrieve all users who are members of the specified team. Access restricted to team members."
)
async def get_team_users(
        team_id: int = Path(..., description="ID of the team"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_team_member)
) -> List[UserRead]:
    """Get all users who are members of the team."""
    return await users_crud.get_team_users(db, team_id)

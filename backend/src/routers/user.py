from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.services.user import users_crud
from backend.src.models import UserRole
from backend.src.schemas import UserCreate, UserRead, UserUpdate, UserReadWithTeams

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    """Get a list of all users."""
    return await users_crud.get_all(db)


@router.get("/{user_id}", response_model=UserReadWithTeams)
async def read_user_detail(user_id: int, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Get a user by ID."""
    return await users_crud.get_with_teams(db, user_id)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Create a new user."""
    return await users_crud.create(db, user_in)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db), ) -> UserRead:
    """Update an existing user."""
    return await users_crud.update(db, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a user by ID."""
    await users_crud.delete(db, user_id)
    return None


@router.put("/{user_id}/set-role", response_model=UserRead)
async def set_user_role(user_id: int, role: UserRole, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Set global role for a user (admin only)."""
    return await users_crud.set_global_role(db, user_id, role)


@router.get("/teams/{team_id}/users", response_model=List[UserRead])
async def get_team_users(team_id: int, db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    """Get all users who are members of the team."""
    return await users_crud.get_team_users(db, team_id)

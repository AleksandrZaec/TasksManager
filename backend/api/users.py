from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.config.db import get_db
from backend.crud.users import UserCRUD
from backend.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter()

user_crud = UserCRUD()


@router.get("/", response_model=List[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)) -> List[UserRead]:
    """
    Get a list of all users.
    """
    users = await user_crud.get_all(db)
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Get a user by ID."""
    user = await user_crud.get_by_id(db, user_id)
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Create a new user."""
    return await user_crud.create(db, user_in)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db), ) -> UserRead:
    """Update an existing user."""
    return await user_crud.update(db, user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a user by ID."""
    await user_crud.delete(db, user_id)
    return None

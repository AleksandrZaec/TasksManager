from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.auth.security import pwd_context
from backend.crud.basecrud import BaseCRUD
from backend.models.user import User
from backend.schemas.user import UserCreate, UserRead, UserUpdate


class UserCRUD(BaseCRUD):
    def __init__(self):
        """Init with User model and UserRead schema."""
        super().__init__(User, UserRead)

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> UserRead:
        """Create user if email not taken, hash password."""
        result = await db.execute(select(User).where(User.email == obj_in.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        password = pwd_context.hash(obj_in.password)

        user_data = obj_in.model_dump(exclude={"password"})
        user = User(**user_data, password=password)

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserRead.model_validate(user)

    async def update(self, db: AsyncSession, obj_id: int, obj_in: UserUpdate) -> UserRead:
        """Update user fields, check email uniqueness."""
        result = await db.execute(select(User).where(User.id == obj_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = obj_in.dict(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            result = await db.execute(select(User).where(User.email == update_data["email"]))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        if "password" in update_data:
            password = pwd_context.hash(update_data.pop("password"))
            user.password = password

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return UserRead.model_validate(user)


users_crud = UserCRUD()

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.src.models import TeamUserAssociation, User, UserRole
from backend.src.utils.security import pwd_context
from backend.src.services.basecrud import BaseCRUD
from backend.src.schemas import UserCreate, UserRead, UserUpdate, UserReadWithTeams, UserTeamRead
from sqlalchemy.orm import selectinload


class UserCRUD(BaseCRUD):
    """CRUD operations for User model."""

    def __init__(self):
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
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        await db.refresh(user)
        return UserRead.model_validate(user)

    async def update(self, db: AsyncSession, user_id: int, user_in: UserUpdate) -> UserRead:
        """Update user fields, check email uniqueness."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_in.model_dump(exclude_unset=True)

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

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        await db.refresh(user)
        return UserRead.model_validate(user)

    @staticmethod
    async def get_for_login(db: AsyncSession, email: str):
        user = await db.scalar(select(User).options(selectinload(User.user_teams).load_only(
            TeamUserAssociation.team_id, TeamUserAssociation.role)).where(User.email == email))

        if not user:
            return None

        user_data = {
            "password": user.password,
            "id": user.id,
            "role": user.role.value,
            "teams": [
                {
                    "team_id": association.team_id,
                    "role": association.role.value
                }
                for association in user.user_teams
            ]
        }

        return user_data

    async def get_with_teams(self, db: AsyncSession, user_id: int) -> UserReadWithTeams:
        """Retrieve a user by ID along with their team memberships and roles, including team names."""
        result = await db.execute(select(User).where(User.id == user_id).options(
            selectinload(User.user_teams).selectinload(TeamUserAssociation.team)))

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserReadWithTeams(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            teams=[
                UserTeamRead(
                    team_id=assoc.team_id,
                    role=assoc.role,
                    team_name=assoc.team.name
                )
                for assoc in user.user_teams
            ]
        )

    async def set_global_role(self, db: AsyncSession, user_id: int, role: UserRole) -> UserRead:
        """Assign a global role to a user (for admins only)."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.role = role
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        await db.refresh(user)
        return UserRead.model_validate(user)

    async def get_team_users(self, db: AsyncSession, team_id: int) -> list[UserRead]:
        """Return all users who belong to a team."""
        stmt = (
            select(User)
            .join(TeamUserAssociation, TeamUserAssociation.user_id == User.id)
            .where(TeamUserAssociation.team_id == team_id))

        result = await db.execute(stmt)
        users = result.scalars().all()
        return [UserRead.model_validate(user) for user in users]


users_crud = UserCRUD()

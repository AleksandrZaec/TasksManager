from typing import List
from backend.src.models import User, TeamUserAssociation, TeamRole
from backend.src.schemas.user import UserRead
from backend.src.services.basecrud import BaseCRUD
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.schemas.team_user import TeamUserAssociationRead, TeamUserAdd
from sqlalchemy import select, delete, update


class TeamUserCRUD(BaseCRUD):
    """CRUD operations for team-user associations."""

    def __init__(self):
        super().__init__(TeamUserAssociation, TeamUserAssociationRead)

    async def add_users_bulk(
            self,
            db: AsyncSession,
            team_id: int,
            users: List[TeamUserAdd],
    ) -> dict:
        """Add multiple users to a team with roles."""
        added_emails = []
        errors = []

        emails = [user.email for user in users]

        stmt = select(User.id, User.email).where(User.email.in_(emails))
        result = await db.execute(stmt)
        existing_users = {email: user_id for user_id, email in result.all()}

        stmt = select(TeamUserAssociation.user_id).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id.in_(existing_users.values()))
        result = await db.execute(stmt)
        existing_assocs = {row[0] for row in result.all()}

        for user_data in users:
            user_id = existing_users.get(user_data.email)
            if user_id is None:
                errors.append(f"User with email {user_data.email} not found")
                continue
            if user_id in existing_assocs:
                errors.append(f"User {user_data.email} is already a member of the team")
                continue

            new_assoc = TeamUserAssociation(
                team_id=team_id,
                user_id=user_id,
                role=user_data.role or TeamRole.EXECUTOR
            )
            db.add(new_assoc)
            added_emails.append(user_data.email)

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return {"added": added_emails, "errors": errors}

    async def remove_user(self, db: AsyncSession, team_id: int, user_id: int) -> None:
        """Remove a user from a team."""
        stmt = delete(TeamUserAssociation).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id == user_id)

        await db.execute(stmt)
        await db.commit()
        return None

    async def update_user_role(self, db: AsyncSession, team_id: int, user_id: int, role: TeamRole) -> dict:
        """Update a user's role inside a team. Raise if not found."""
        stmt = (update(TeamUserAssociation).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id == user_id
        ).values(role=role).execution_options(synchronize_session="fetch"))

        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of the team")

        return {"msg": "User role updated"}

    async def get_team_users(self, db: AsyncSession, team_id: int) -> list[UserRead]:
        """Return all users who belong to a team."""
        stmt = (
            select(User)
            .join(TeamUserAssociation, TeamUserAssociation.user_id == User.id)
            .where(TeamUserAssociation.team_id == team_id)
        )

        result = await db.execute(stmt)
        users = result.scalars().all()
        return [UserRead.model_validate(user) for user in users]


team_users_crud = TeamUserCRUD()

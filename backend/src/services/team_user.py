from backend.src.services.basecrud import BaseCRUD
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Dict
from backend.src.models.association import TeamUserAssociation, TeamRole
from backend.src.schemas.team_user import TeamUserAssociationRead


class TeamUserAssociationCRUD(BaseCRUD):
    """CRUD operations for team-user associations."""

    def __init__(self):
        super().__init__(TeamUserAssociation, TeamUserAssociationRead)

    async def add_user(self, db: AsyncSession, team_id: int, user_id: int,
                       role: TeamRole) -> TeamUserAssociationRead:
        """Add a user to a team with a specific role."""
        association = TeamUserAssociation(team_id=team_id, user_id=user_id, role=role)
        db.add(association)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="User is already in the team")

        await db.refresh(association)
        return TeamUserAssociationRead.model_validate(association)

    async def remove_user(
            self, db: AsyncSession, team_id: int, user_id: int
    ) -> Dict[str, str]:
        """Remove a user from a team."""
        result = await db.execute(
            select(TeamUserAssociation).where(
                TeamUserAssociation.team_id == team_id,
                TeamUserAssociation.user_id == user_id
            )
        )
        association = result.scalar_one_or_none()
        if not association:
            raise HTTPException(status_code=404, detail="User is not in the team")

        await db.delete(association)
        await db.commit()
        return {"message": "User removed from team"}

    async def update_user_role(
            self, db: AsyncSession, team_id: int, user_id: int, role: TeamRole
    ) -> TeamUserAssociationRead:
        """Update a user's role in a team."""
        result = await db.execute(
            select(TeamUserAssociation).where(
                TeamUserAssociation.team_id == team_id,
                TeamUserAssociation.user_id == user_id
            )
        )
        association = result.scalar_one_or_none()
        if not association:
            raise HTTPException(status_code=404, detail="User is not in the team")

        association.role = role
        await db.commit()
        await db.refresh(association)
        return TeamUserAssociationRead.model_validate(association)


team_user_association_crud = TeamUserAssociationCRUD()


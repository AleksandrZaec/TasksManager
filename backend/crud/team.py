from datetime import datetime, timedelta, timezone
from backend.models.team import Team
from backend.schemas.team import TeamRead, TeamCreate
from backend.crud.basecrud import BaseCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select


class TeamCRUD(BaseCRUD):
    """CRUD operations for Team model."""

    def __init__(self):
        super().__init__(Team, TeamRead)

    async def create(self, db: AsyncSession, team: TeamCreate) -> Team:
        """Creates a team, guaranteed to set the deadline for the invite code."""
        team_data = team.model_dump()

        if team_data.get("invite_code_expires_at") is None:
            team_data["invite_code_expires_at"] = datetime.now(timezone.utc) + timedelta(days=7)

        team = Team(**team_data)
        db.add(team)
        await db.commit()
        await db.refresh(team)
        return team

    async def get_team(self, db: AsyncSession, team_id: int) -> Team | None:
        """Get team with preloaded team_users relationship"""
        result = await db.execute(
            select(Team)
            .options(selectinload(Team.team_users))
            .where(Team.id == team_id)
        )
        return result.scalar_one_or_none()


team_crud = TeamCRUD()

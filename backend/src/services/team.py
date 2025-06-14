import uuid
from datetime import datetime, timedelta, timezone
from backend.src.models.team import Team
from backend.src.schemas.team import TeamCreate, TeamRead, TeamWithUsersAndTask
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload


class TeamCRUD(BaseCRUD):
    """CRUD operations for Team model."""

    def __init__(self):
        super().__init__(Team, TeamRead)

    def _generate_invite_code(self, name: str) -> str:
        """Generate invite code from team name plus 4 digits from UUID4."""
        clean_name = name.replace(" ", "").upper()
        unique_digits = str(uuid.uuid4().int)[:4]
        return f"{clean_name}-{unique_digits}"

    async def create(self, db: AsyncSession, team: TeamCreate) -> TeamRead:
        """Create a new Team ensuring unique name, with fallback on DB constraint."""
        result = await db.execute(
            select(Team).where(Team.name == team.name.strip())
        )
        existing_team = result.scalar_one_or_none()
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team with this name already exists"
            )

        team_data = team.model_dump()
        team_data["name"] = team_data["name"].strip()

        if team_data.get("invite_code_expires_at") is None:
            team_data["invite_code_expires_at"] = datetime.now(timezone.utc) + timedelta(days=7)

        max_attempts = 5
        for attempt in range(max_attempts):
            team_data["invite_code"] = self._generate_invite_code(team_data["name"])
            team = Team(**team_data)
            db.add(team)
            try:
                await db.commit()
                await db.refresh(team)
                return TeamRead.model_validate(team)
            except IntegrityError as e:
                await db.rollback()
                err_msg = str(e.orig).lower()
                if "teams_name_key" in err_msg or ("unique constraint" in err_msg and "name" in err_msg):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Team with this name already exists"
                    )
                elif "teams_invite_code_key" in err_msg or (
                        "unique constraint" in err_msg and "invite_code" in err_msg):
                    if attempt == max_attempts - 1:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to generate unique invite code, please try again"
                        )
                else:
                    raise

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create team after multiple attempts"
        )

    async def get_by_id_with_relations(self, db: AsyncSession, team_id: int) -> TeamWithUsersAndTask:
        """Get team by id with related users and tasks loaded via selectinload."""
        stmt = (
            select(Team)
            .options(
                selectinload(Team.team_users),
                selectinload(Team.tasks)
            )
            .where(Team.id == team_id)
        )
        result = await db.execute(stmt)
        team = result.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return TeamWithUsersAndTask.model_validate(team)


team_crud = TeamCRUD()


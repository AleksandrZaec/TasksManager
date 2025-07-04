from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Enum as SQLEnum, DateTime
from src.config.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.enum import UserRole, TeamRole


class TeamUserAssociation(Base):
    """
    Association model for the many-to-many relationship between users and teams.
    Stores the user's role in the team and timestamps.
    """
    __tablename__ = "team_user_association"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(TeamRole), default=TeamRole.EXECUTOR)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    team: Mapped["Team"] = relationship(back_populates="team_users")
    user: Mapped["User"] = relationship(back_populates="user_teams")

    def __str__(self):
        return f"User {self.user_id} in team {self.team_id} as {self.role}"


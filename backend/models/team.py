from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.config.db import Base
from sqlalchemy import Text, String
from sqlalchemy.dialects import postgresql


class Team(Base):
    """Team model representing a group with a name, optional description, and associated members."""
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    invite_code_expires_at: Mapped[datetime] = mapped_column(postgresql.TIMESTAMP(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    team_users: Mapped[List["TeamUserAssociation"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="team",
        cascade="all, delete-orphan"
    )

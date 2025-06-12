from datetime import datetime
from sqlalchemy import ForeignKey, Enum as SQLEnum, String
from backend.config.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models.enums import UserRole


class TeamUserAssociation(Base):
    """
    Association model for the many-to-many relationship between users and teams.
    Stores the user's role in the team and timestamps.
    """
    __tablename__ = "team_user_association"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship(back_populates="team_users")
    user: Mapped["User"] = relationship(back_populates="user_teams")

    def __str__(self):
        return f"User {self.user_id} in team {self.team_id} as {self.role}"


class TaskAssigneeAssociation(Base):
    """
    Association table for the many-to-many relationship between tasks and assignees.
    Allows multiple users to be assigned to a single task.
    """
    __tablename__ = "task_assignee_association"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    assigned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    role: Mapped[str] = mapped_column(String(20), nullable=True)

    task: Mapped["Task"] = relationship(back_populates="assignee_associations")
    user: Mapped["User"] = relationship(back_populates="task_associations")

    def __str__(self):
        return f"TaskAssignee: task_id={self.task_id}, user_id={self.user_id}, role={self.role}"


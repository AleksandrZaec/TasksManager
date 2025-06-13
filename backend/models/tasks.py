from typing import List, Optional
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Enum, ForeignKey, DateTime, Text, String
from datetime import datetime, timezone
from backend.config.db import Base
from backend.models.enums import TaskStatus, TaskPriority


class Task(Base):
    """
    Task model representing a task with title, description, creator, assignees,
    status, deadline, comments, and evaluation.
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.OPEN, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team: Mapped["Team"] = relationship("Team", back_populates="tasks")
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee_associations: Mapped[List["TaskAssigneeAssociation"]] = relationship(back_populates="task")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    assignees: Mapped[List["User"]] = relationship(
        "User",
        secondary="task_assignee_association",
        back_populates="assigned_tasks"
    )

    evaluations: Mapped[List["Evaluation"]] = relationship(
        "Evaluation",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )

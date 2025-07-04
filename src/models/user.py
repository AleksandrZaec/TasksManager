from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Enum, String, Boolean
from typing import List
from src.config.db import Base
from src.models.enum import UserRole


class User(Base):
    """
    User model representing an application user with personal info, role,
    and relationships to tasks, teams, comments, and meetings.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        cascade="save-update, merge"
    )

    user_teams: Mapped[List["TeamUserAssociation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    evaluations_given: Mapped[List["Evaluation"]] = relationship(
        "Evaluation",
        back_populates="evaluator",
    )

    received_evaluations: Mapped[List["EvaluationAssociation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    created_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        foreign_keys="[Task.creator_id]",
        back_populates="creator",
        cascade="save-update, merge"
    )

    task_associations: Mapped[List["TaskAssigneeAssociation"]] = relationship(
        back_populates="user",
        overlaps="assigned_tasks"
    )

    meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting",
        secondary="meeting_participant_association",
        back_populates="participants"
    )

    cancelled_meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting",
        foreign_keys="[Meeting.cancelled_by_id]",
        back_populates="cancelled_by"
    )

    created_meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting",
        foreign_keys="[Meeting.creator_id]",
        back_populates="creator",
        cascade="save-update, merge"
    )

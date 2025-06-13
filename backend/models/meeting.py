from sqlalchemy import ForeignKey, Enum, DateTime, String, Text, CheckConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from backend.config.db import Base
from backend.models.enum import MeetingStatus
from datetime import datetime, timezone


class Meeting(Base):
    """Meeting model representing a scheduled event with participants, creator, and cancellation metadata."""
    __tablename__ = "meetings"
    __table_args__ = (
        CheckConstraint('end_datetime > start_datetime', name='check_meeting_times'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus),
        default=MeetingStatus.SCHEDULED,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[creator_id],
        back_populates="created_meetings"
    )
    cancelled_by: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[cancelled_by_id],
        back_populates="cancelled_meetings"
    )
    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary="meeting_participant_association",
        back_populates="meetings"
    )

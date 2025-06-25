from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Column, DateTime, Integer
from src.config.db import Base


class MeetingParticipantAssociation(Base):
    """
    Association table for the many-to-many relationship between meetings and participants.
    Each row represents a user's participation in a meeting.
    """
    __tablename__ = "meeting_participant_association"

    meeting_id = Column(Integer, ForeignKey("meetings.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

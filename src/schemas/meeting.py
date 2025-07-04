from pydantic import BaseModel, model_validator, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from src.models.enum import MeetingStatus
from src.schemas.team_user import AddedUserInfo


class MeetingCreate(BaseModel):
    """Scheme for creating a meeting"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    participant_ids: Optional[List[int]] = None

    @model_validator(mode='before')
    def check_dates(cls, values):
        start = values.get('start_datetime')
        end = values.get('end_datetime')
        if start and end and end <= start:
            raise ValueError('end_datetime must be after start_datetime')
        return values


class MeetingShortRead(BaseModel):
    """Brief overview of the meeting (list)"""
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    status: MeetingStatus
    location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeetingRead(MeetingShortRead):
    """Detailed viewing scheme for one meeting"""
    creator: AddedUserInfo
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[AddedUserInfo] = None
    participants: List[AddedUserInfo]

    model_config = ConfigDict(from_attributes=True)


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MeetingStatus] = None
    location: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    add_participant_ids: List[int] = Field(default_factory=list)
    remove_participant_ids: List[int] = Field(default_factory=list)

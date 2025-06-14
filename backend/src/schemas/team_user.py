from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.src.models.enum import TeamRole


class TeamUserAssociationBase(BaseModel):
    """Base schema for team-user association."""
    team_id: int
    user_id: int
    role: TeamRole


class TeamUserAssociationCreate(TeamUserAssociationBase):
    """Schema for adding a user to a team."""
    pass


class TeamUserAssociationUpdate(TeamUserAssociationBase):
    """Schema for updating team-user association role."""
    role: Optional[TeamRole] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None


class TeamUserAssociationRead(TeamUserAssociationBase):
    """Schema for reading team-user association with timestamps."""
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




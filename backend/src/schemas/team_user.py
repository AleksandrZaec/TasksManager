from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.src.models.enum import TeamRole


class TeamUserAssociationBase(BaseModel):
    """Base schema for team-user association."""
    team_id: int
    user_id: int
    role: TeamRole


class TeamUserAssociationCreate(TeamUserAssociationBase):
    """Schema for creating a team-user association."""
    pass


class TeamUserAssociationUpdate(BaseModel):
    """Schema for updating team-user association fields."""
    role: Optional[TeamRole] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None


class TeamUserAssociationRead(BaseModel):
    """Detailed team user info (flat structure)"""
    user_id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: TeamRole
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamUserAdd(BaseModel):
    """Payload for adding a user to a team by email and role."""
    email: EmailStr
    role: TeamRole = TeamRole.EXECUTOR


class TeamUserUpdateRole(BaseModel):
    """Payload for updating a user's role in a team."""
    role: TeamRole

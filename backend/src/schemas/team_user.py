from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from backend.src.models.enum import TeamRole


class TeamUserAdd(BaseModel):
    """Payload for adding a user to a team by user ID and role."""
    user_id: int
    role: TeamRole = TeamRole.EXECUTOR


class TeamUsersCreate(BaseModel):
    """Payload for bulk adding users to a team."""
    users: List[TeamUserAdd]


class AddedUserInfo(BaseModel):
    """Information about a user successfully added to the team."""
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamUserUpdateRole(BaseModel):
    """Payload for updating a user's role in a team."""
    role: TeamRole


class TeamUserAssociationRead(BaseModel):
    """Detailed team user info with timestamps."""
    user_id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: TeamRole
    joined_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

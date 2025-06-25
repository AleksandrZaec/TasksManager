import re
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from src.schemas.task import TaskRead
from src.schemas.team_user import TeamUserAssociationRead, TeamUserAdd
from datetime import datetime


class TeamBase(BaseModel):
    """Common fields and validation for a team."""
    name: str = Field(..., max_length=50, min_length=1)
    description: Optional[str] = Field(default=None, max_length=200)

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate team name."""
        v = v.strip()
        if not v:
            raise ValueError("Team name cannot be empty or whitespace only")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\- _]+$', v):
            raise ValueError(
                "Only letters (English/Russian), numbers, hyphens, spaces and underscores are allowed"
            )
        return v

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    description: str = Field(..., max_length=200)
    users: Optional[List[TeamUserAdd]] = None

    @field_validator("users")
    def check_unique_user_ids(cls, users):
        if users is None:
            return users
        user_ids = [u.user_id for u in users]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("Duplicate user_id in users")
        return users


class TeamUpdate(BaseModel):
    """Schema for update a team."""
    name: Optional[str] = None
    description: Optional[str] = None
    invite_code_expires_at: Optional[datetime] = None


class TeamRead(BaseModel):
    """Basic schema for reading team information."""
    id: int
    name: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TeamWithUsersAndTask(TeamRead):
    """Team with related users and tasks."""
    team_users: List[TeamUserAssociationRead] = Field(default_factory=list)
    tasks: List[TaskRead] = Field(default_factory=list)

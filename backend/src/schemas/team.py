import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from backend.src.schemas.task import TaskRead
from backend.src.schemas.team_user import TeamUserAssociationRead


class TeamBase(BaseModel):
    """Shared fields and validation logic for a team."""
    name: str = Field(..., max_length=50, min_length=1)
    description: Optional[str] = Field(default=None, max_length=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Team name cannot be empty or whitespace only")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\- _]+$', v):
            raise ValueError(
                "Only letters (English/Russian), numbers, hyphens, spaces and underscores are allowed"
            )
        return v

    class Config:
        str_strip_whitespace = True


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    description: str = Field(..., max_length=200)


class TeamUpdate(BaseModel):
    """Schema for updating team fields."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class TeamRead(BaseModel):
    """Basic team info for responses."""
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class TeamWithUsersAndTask(TeamRead):
    """Team info with related users and tasks."""
    team_users: List[TeamUserAssociationRead] = Field(default_factory=list)
    tasks: List[TaskRead] = Field(default_factory=list)

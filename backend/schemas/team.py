import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

from backend.schemas.task import TaskRead
from backend.schemas.team_user import TeamUserAssociationRead


class TeamBase(BaseModel):
    """Base model for team with validation"""
    name: str = Field(
        ...,
        max_length=50,
        min_length=1,
        examples=["My Team", "Моя команда"],
        description="Team name (1-50 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=200,
        examples=["Team description"],
        description="Optional team description"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validates team name:
        1. Strips whitespace
        2. Checks for empty string
        3. Validates allowed characters
        """
        stripped = v.strip()

        if not stripped:
            raise ValueError("Team name cannot be empty or whitespace only")
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\- _]+$', stripped):
            raise ValueError(
                "Only letters (English/Russian), numbers, hyphens, spaces and underscores are allowed"
            )

        return stripped

    class Config:
        str_strip_whitespace = True
        str_min_length = 1


class TeamCreate(TeamBase):
    """Fields for creating a team. """
    pass


class TeamUpdate(BaseModel):
    """Fields allowed to update a team."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamReadBase(BaseModel):
    """Base response without detailed relationships"""
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    invite_code_expires_at: Optional[datetime]
    is_active: bool


class TeamRead(TeamReadBase):
    """Full response with relationships"""
    team_users: List[TeamUserAssociationRead] = Field(default_factory=list)
    tasks: List[TaskRead] = Field(default_factory=list)

    class Config:
        from_attributes = True

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List
from backend.schemas.TeamUserAssociation_schemas import TeamUserAssociationRead


class TeamBase(BaseModel):
    """Base fields shared by all team schemas."""
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    invite_code: str = Field(..., max_length=20)
    invite_code_expires_at: Optional[datetime] = None
    is_active: bool = True


class TeamCreate(TeamBase):
    """Fields required to create a new team."""
    pass


class TeamUpdate(BaseModel):
    """Fields allowed to update a team."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    invite_code: Optional[str] = Field(None, max_length=20)
    invite_code_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class TeamRead(TeamBase):
    """Fields returned in team read responses."""
    id: int
    team_users: List[TeamUserAssociationRead] = []

    class Config:
        from_attributes = True



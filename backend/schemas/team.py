from pydantic import BaseModel, Field, field_validator
from typing import Optional
from typing import List
from backend.schemas.team_user import TeamUserAssociationRead
from datetime import datetime, timezone


class TeamBase(BaseModel):
    """Base fields shared by all team schemas."""
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    invite_code: str = Field(..., max_length=20)
    invite_code_expires_at: Optional[datetime] = None
    is_active: bool = True


class TeamCreate(TeamBase):
    invite_code_expires_at: datetime | None = Field(
        None,
        description="Автоматически: текущее время +7 дней"
    )

    @field_validator('invite_code_expires_at')
    @classmethod
    def validate_future_date(cls, v):
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Дата должна быть в будущем")
        return v


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

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
import re
from src.models.enum import TeamRole
from src.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: Optional[str] = Field(max_length=20)
    last_name: Optional[str] = Field(max_length=20)
    role: UserRole = UserRole.USER


class UserTeamInfo(BaseModel):
    """Schema describing the user's role within a team (used in JWT)."""
    team_id: int
    role: TeamRole


class UserTeamRead(UserTeamInfo):
    """User role in a team with team name (for detailed API responses)."""
    team_name: str


class UserRead(UserBase):
    """Schema for reading basic user data from the database."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserReadWithTeams(UserRead):
    """Schema for reading user data with all team roles and team names."""
    teams: List[UserTeamRead] = []

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    first_name: Optional[str] = Field(max_length=20)
    last_name: Optional[str] = Field(max_length=20)
    password: str

    @field_validator('password')
    def password_strong(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise ValueError('Password must contain at least one special character')
        return value


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

    @field_validator('password')
    def password_strong(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise ValueError('Password must contain at least one special character')
        return value


class UserPayload(BaseModel):
    """The payload model for the JWT token."""
    id: int
    role: str
    teams: List[UserTeamInfo] = Field(default_factory=list)

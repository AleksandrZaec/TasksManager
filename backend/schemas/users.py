from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re
from backend.models.users import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: Optional[str] = Field(max_length=20)
    last_name: Optional[str] = Field(max_length=20)
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

    @field_validator('password')
    @classmethod
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
    role: Optional[UserRole] = None
    password: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data from the database."""
    id: int

    class Config:
        from_attributes = True


class UserNameOnly(BaseModel):
    """Schema for the presentation in the tasks"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True
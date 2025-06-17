from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from backend.src.models import TeamRole


class AssigneeInfo(BaseModel):
    """Base schema for task assignee information."""
    email: str
    role: Optional[str] = None
    assigned_at: datetime

    class Config:
        from_attributes = True


class TaskUserAdd(BaseModel):
    """User email and optional role for task assignment."""
    email: EmailStr
    role: Optional[str] = None


class TaskAssigneeCreate(BaseModel):
    """List of users to assign to a task."""
    users: List[TaskUserAdd]


class TaskAssigneeRead(AssigneeInfo):
    """Schema for reading task assignee"""
    assigned_at: datetime




class RoleUpdatePayload(BaseModel):
    """For update role executor in task"""
    new_role: str



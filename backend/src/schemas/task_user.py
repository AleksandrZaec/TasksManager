from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AssigneeInfo(BaseModel):
    """Base schema for task assignee information."""
    email: str
    role: Optional[str] = None
    assigned_at: datetime

    class Config:
        from_attributes = True


class TaskAssigneeCreate(BaseModel):
    """Schema for creating a task-assignee association."""
    user_id: int
    role: Optional[str] = None


class TaskAssigneeRead(AssigneeInfo):
    """Schema for reading task assignee"""
    assigned_at: datetime


class RoleUpdatePayload(BaseModel):
    """For update role executor in task"""
    new_role: str


from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.models.enum import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base schema for a task with common fields."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    team_id: int


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    """Schema for reading task data, including metadata."""
    id: int
    creator_id: int
    team_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

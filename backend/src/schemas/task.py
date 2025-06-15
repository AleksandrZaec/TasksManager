from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from backend.src.models.enum import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base schema for tasks used for shared fields."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    team_id: int

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskShortRead(BaseModel):
    """Schema for listing tasks."""
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    id: int

    class Config:
        from_attributes = True


class TaskRead(TaskBase):
    """Detailed schema for a task, includes assignees and creator email."""
    id: int
    creator_email: str
    created_at: datetime
    updated_at: Optional[datetime]
    assignees: List[str] = []

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    """Schema for update status."""
    status: TaskStatus


class TaskFilter(BaseModel):
    """Schema for filters for user-related tasks."""
    statuses: Optional[List[TaskStatus]] = None
    priorities: Optional[List[TaskPriority]] = None
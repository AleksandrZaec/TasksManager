from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator
from backend.src.models.enum import TaskStatus, TaskPriority
from backend.src.schemas.task_user import AssigneeInfo, TaskUserAdd


class TaskBase(BaseModel):
    """Base schema for tasks used for shared fields."""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    assignees: Optional[List[TaskUserAdd]] = None

    @field_validator("assignees")
    @classmethod
    def check_unique_user_ids(cls, assignees):
        if assignees is None:
            return assignees
        user_ids = [a.user_id for a in assignees]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("Duplicate user_id in assignees")
        return assignees


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None


class TaskShortRead(BaseModel):
    """Schema for listing tasks."""
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    id: int

    class Config:
        from_attributes = True


class TaskRead(TaskBase):
    """Detailed schema for a task, includes assignees with role and assigned time."""
    id: int
    team_id: int
    creator_email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    assignees: List[AssigneeInfo] = []

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    """Schema for update status."""
    status: TaskStatus


class TaskFilter(BaseModel):
    """Schema for filters for user-related tasks."""
    statuses: Optional[List[TaskStatus]] = None
    priorities: Optional[List[TaskPriority]] = None
    team_id: Optional[int] = None

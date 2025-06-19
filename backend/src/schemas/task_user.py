from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from backend.src.schemas.team_user import AddedUserInfo


class AssigneeInfo(BaseModel):
    """Base schema for task assignee information."""
    id: int
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = None
    assigned_at: datetime

    class Config:
        from_attributes = True


class TaskUserAdd(BaseModel):
    """User ID and optional role for task assignment."""
    user_id: int
    role: Optional[str] = None


class TaskAssigneeCreate(BaseModel):
    """List of users to assign to a task."""
    users: List[TaskUserAdd]


class RoleUpdatePayload(BaseModel):
    """For update role executor in task"""
    new_role: str


class RoleUpdateResponse(BaseModel):
    """For update role executor in task"""
    msg: str



class AddUsersResponse(BaseModel):
    """Response schema for adding users to a task or team, including successes and errors."""
    added: List[AddedUserInfo]
    errors: List[str]


class UsersRemoveRequest(BaseModel):
    """Request schema for removing executors from a task by their user IDs."""
    user_ids: List[int]


class UsersRemoveResponse(BaseModel):
    """Response schema after removing executors, listing removed and not found user IDs."""
    removed: List[int]
    not_found: List[int]

    class Config:
        from_attributes = True

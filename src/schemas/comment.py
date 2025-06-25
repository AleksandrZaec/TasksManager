from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    """Base schema for comment."""
    content: str


class CommentRead(CommentBase):
    """Schema for read comment."""
    id: int
    created_at: datetime
    author_full_name: str
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class CommentUpdate(BaseModel):
    """Schema for update comment"""
    content: str

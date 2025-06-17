from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EvaluationCreate(BaseModel):
    """Schema for creating a task evaluation."""
    score: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


class EvaluationRead(BaseModel):
    """Schema for reading a task evaluation."""
    id: int
    task_id: int
    evaluator_id: int
    score: int
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    evaluator_full_name: Optional[str] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MeetingCreate(BaseModel):
    """Schema for creating a meeting."""
    title: str
    description: str
    location: str
    start_datetime: datetime
    end_datetime: datetime
    participant_ids: Optional[List[int]] = None

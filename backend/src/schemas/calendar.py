from pydantic import BaseModel
from typing import Union, List
from datetime import datetime, date


class CalendarTask(BaseModel):
    type: str = "task"
    id: int
    title: str
    due_date: date


class CalendarMeeting(BaseModel):
    type: str = "meeting"
    id: int
    title: str
    start_datetime: datetime
    end_datetime: datetime


CalendarEvent = Union[CalendarTask, CalendarMeeting]

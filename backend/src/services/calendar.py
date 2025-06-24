from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
import asyncio
from collections import defaultdict
from datetime import date
from typing import Dict, List
from backend.src.models import Task, TaskAssigneeAssociation, Meeting, TeamUserAssociation, User
from backend.src.schemas.calendar import CalendarEvent, CalendarTask, CalendarMeeting


async def get_user_calendar(
        db: AsyncSession,
        start_date: date,
        end_date: date,
        user_id: int,
) -> Dict[date, List[CalendarEvent]]:
    """Fetches user's tasks and meetings within a date range with optimized queries."""
    task_stmt, meeting_stmt = (
        select(Task).distinct()
        .where(
            Task.due_date.between(start_date, end_date),
            or_(
                Task.creator_id == user_id,
                Task.assignee_associations.any(TaskAssigneeAssociation.user_id == user_id)))
        .options(selectinload(Task.assignee_associations)),

        select(Meeting).distinct()
        .where(
            Meeting.start_datetime.between(start_date, end_date),
            Meeting.participants.any(id=user_id))
        .options(selectinload(Meeting.participants)))

    task_result, meeting_result = await asyncio.gather(
        db.execute(task_stmt),
        db.execute(meeting_stmt))

    tasks = task_result.scalars().all()
    meetings = meeting_result.scalars().all()

    calendar: Dict[date, List[CalendarEvent]] = defaultdict(list)

    for task in tasks:
        if task.due_date:
            calendar[task.due_date.date()].append(CalendarTask(
                id=task.id,
                title=task.title,
                due_date=task.due_date.date()))

    for meeting in meetings:
        calendar[meeting.start_datetime.date()].append(CalendarMeeting(
            id=meeting.id,
            title=meeting.title or "Untitled",
            start_datetime=meeting.start_datetime,
            end_datetime=meeting.end_datetime))

    for events in calendar.values():
        events.sort(
            key=lambda e: e.due_date if isinstance(e, CalendarTask) else e.start_datetime.date())

    return dict(calendar)


async def get_team_calendar(
        db: AsyncSession,
        team_id: int,
        start_date: date,
        end_date: date,
) -> Dict[date, List[CalendarEvent]]:
    """Retrieve team calendar events with optimized single-query approach for meetings."""
    task_stmt, meeting_stmt = (
        select(Task)
        .where(
            Task.team_id == team_id,
            Task.due_date.between(start_date, end_date))
        .options(selectinload(Task.assignee_associations)),

        select(Meeting).distinct()
        .join(Meeting.participants)
        .join(TeamUserAssociation, TeamUserAssociation.user_id == User.id)
        .where(
            Meeting.start_datetime.between(start_date, end_date),
            TeamUserAssociation.team_id == team_id)
        .options(selectinload(Meeting.participants)))

    task_result, meeting_result = await asyncio.gather(
        db.execute(task_stmt),
        db.execute(meeting_stmt))

    tasks = task_result.scalars().all()
    meetings = meeting_result.scalars().all()

    calendar: Dict[date, List[CalendarEvent]] = defaultdict(list)

    for task in tasks:
        if task.due_date:
            calendar[task.due_date.date()].append(CalendarTask(
                id=task.id,
                title=task.title,
                due_date=task.due_date.date()))

    for meeting in meetings:
        calendar[meeting.start_datetime.date()].append(CalendarMeeting(
            id=meeting.id,
            title=meeting.title or "Untitled",
            start_datetime=meeting.start_datetime,
            end_datetime=meeting.end_datetime))

    for events in calendar.values():
        events.sort(key=lambda e: e.due_date if isinstance(e, CalendarTask) else e.start_datetime.date())

    return dict(calendar)


from datetime import date
from typing import Dict, List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.db import get_db
from src.deps.permissions import is_team_member
from src.models import User
from src.schemas import UserPayload
from src.schemas.calendar import CalendarEvent
from src.services.auth import get_current_user
from src.services.calendar import get_user_calendar, get_team_calendar

router = APIRouter()


@router.get(
    "/",
    response_model=Dict[date, List[CalendarEvent]],
    summary="Get current user's calendar",
    description=(
        "Retrieve tasks and meetings of the current user within the specified date range. "
        "Events are grouped by date."
    )
)
async def user_calendar(
        start_date: date = Query(..., description="Start date for calendar range (inclusive)"),
        end_date: date = Query(..., description="End date for calendar range (inclusive)"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> Dict[date, List[CalendarEvent]]:
    """Get current user's tasks and meetings grouped by date in the given range."""
    return await get_user_calendar(db, start_date, end_date, current_user.id)


@router.get(
    "/teams/{team_id}/calendar",
    response_model=Dict[date, List[CalendarEvent]],
    summary="Get team's calendar",
    description=(
        "Retrieve calendar events for the specified team within the date range, "
        "grouped by date. Access restricted to team members."
    )
)
async def team_calendar(
        team_id: int = Path(..., description="ID of the team"),
        start_date: date = Query(..., description="Start date for calendar range (inclusive)"),
        end_date: date = Query(..., description="End date for calendar range (inclusive)"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(is_team_member),
) -> Dict[date, List[CalendarEvent]]:
    """Get calendar events of a team grouped by date within the specified range."""
    return await get_team_calendar(db, team_id, start_date, end_date)
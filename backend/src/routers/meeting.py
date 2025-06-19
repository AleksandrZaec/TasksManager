from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models import User
from backend.src.schemas import MeetingShortRead, MeetingCreate, MeetingUpdate, MeetingRead
from backend.src.services.auth import get_current_user
from backend.src.config.db import get_db
from backend.src.services.meeting import meeting_crud

router = APIRouter()


@router.post("/", response_model=MeetingShortRead, status_code=status.HTTP_201_CREATED)
async def create_meeting(
        meet_in: MeetingCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> MeetingShortRead:
    """Create a new meeting."""
    return await meeting_crud.create_meet(db, meet_in, current_user.id)


@router.patch("/{meeting_id}", response_model=MeetingShortRead, status_code=status.HTTP_200_OK)
async def update_meeting(
        meeting_id: int,
        meet_in: MeetingUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> MeetingShortRead:
    """Update meeting."""
    return await meeting_crud.update_meet(db, meeting_id, meet_in, current_user.id)


@router.get("/me_meetings", response_model=List[MeetingShortRead])
async def get_my_meetings(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[MeetingShortRead]:
    """Get all appointments of the current user."""
    return await meeting_crud.get_user_meetings(db, current_user.id)


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting_by_id(meeting_id: int, db: AsyncSession = Depends(get_db)) -> MeetingRead:
    """Get detailed information about the meeting."""
    return await meeting_crud.get_by_id_detailed(db, meeting_id)


@router.get("/meetings/", response_model=List[MeetingShortRead], status_code=status.HTTP_200_OK)
async def get_all_meetings(db: AsyncSession = Depends(get_db), ) -> List[MeetingShortRead]:
    """Get all meetings."""
    return await meeting_crud.get_all(db)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_db), ) -> None:
    """Delete meeting"""
    return await meeting_crud.delete(db, meeting_id)

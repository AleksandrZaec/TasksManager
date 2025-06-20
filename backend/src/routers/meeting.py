from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.deps.permissions import admin_or_manager, creator_or_superuser
from backend.src.models import User, Meeting
from backend.src.schemas import MeetingShortRead, MeetingCreate, MeetingUpdate, MeetingRead, UserPayload
from backend.src.services.auth import get_current_user
from backend.src.config.db import get_db
from backend.src.services.meeting import meeting_crud

router = APIRouter()


@router.post(
    "/",
    response_model=MeetingShortRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meeting",
    description="Create a new meeting. Only admins or team managers can create meetings."
)
async def create_meeting(
        meet_in: MeetingCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_or_manager)
) -> MeetingShortRead:
    """Create a new meeting."""
    return await meeting_crud.create_meet(db, meet_in, current_user.id)


@router.patch(
    "/{meeting_id}",
    response_model=MeetingShortRead,
    status_code=status.HTTP_200_OK,
    summary="Update a meeting",
    description="Update meeting details by meeting ID. Only the meeting creator or a superuser can update."
)
async def update_meeting(
        meeting_id: int = Path(..., description="ID of the meeting to update"),
        meet_in: MeetingUpdate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(creator_or_superuser(Meeting, id_path_param="meeting_id"))
) -> MeetingShortRead:
    """Update meeting."""
    return await meeting_crud.update_meet(db, meeting_id, meet_in, current_user.id)


@router.get(
    "/me_meetings",
    response_model=List[MeetingShortRead],
    summary="Get current user's meetings",
    description="Get all meetings where the current user participates."
)
async def get_my_meetings(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[MeetingShortRead]:
    """Get all appointments of the current user."""
    return await meeting_crud.get_user_meetings(db, current_user.id)


@router.get(
    "/{meeting_id}",
    response_model=MeetingRead,
    summary="Get meeting details by ID",
    description="Retrieve detailed information about a meeting by its ID."
)
async def get_meeting_by_id(
        meeting_id: int = Path(..., description="ID of the meeting"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> MeetingRead:
    """Get detailed information about the meeting."""
    return await meeting_crud.get_by_id_detailed(db, meeting_id)


@router.get(
    "/meetings/",
    response_model=List[MeetingShortRead],
    status_code=status.HTTP_200_OK,
    summary="Get all meetings",
    description="Get a list of all meetings. Only admins or managers can access this endpoint."
)
async def get_all_meetings(
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(admin_or_manager)
) -> List[MeetingShortRead]:
    """Get all meetings."""
    return await meeting_crud.get_all(db)


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meeting",
    description="Delete a meeting by ID. Only the meeting creator or a superuser can delete."
)
async def delete_meeting(
        meeting_id: int = Path(..., description="ID of the meeting to delete"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(creator_or_superuser(Meeting, id_path_param="meeting_id"))
) -> None:
    """Delete meeting"""
    await meeting_crud.delete(db, meeting_id)
    return None

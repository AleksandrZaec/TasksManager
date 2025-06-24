from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from backend.src.models import User, Meeting, MeetingStatus
from backend.src.schemas import MeetingShortRead, MeetingCreate, MeetingUpdate, MeetingRead
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone


class MeetingCRUD(BaseCRUD):
    """CRUD for model Meeting"""

    def __init__(self):
        super().__init__(Meeting, MeetingShortRead)

    async def create_meet(self, db: AsyncSession, meet_in: MeetingCreate, creator_id: int) -> MeetingShortRead:
        """Create a meeting with verification of the existence of participants and time conflicts."""
        participant_ids = set(meet_in.participant_ids or [])
        participant_ids.add(creator_id)
        participant_ids = list(participant_ids)

        result = await db.execute(select(User.id).where(User.id.in_(participant_ids)))
        existing_user_ids = set(row[0] for row in result.all())
        missing_user_ids = set(participant_ids) - existing_user_ids
        if missing_user_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Users with IDs {list(missing_user_ids)} do not exist.")

        result = await db.execute(
            select(User.id)
            .join(User.meetings)
            .where(
                User.id.in_(participant_ids),
                Meeting.status == MeetingStatus.SCHEDULED,
                or_(
                    and_(Meeting.start_datetime <= meet_in.start_datetime,
                         Meeting.end_datetime > meet_in.start_datetime),
                    and_(Meeting.start_datetime < meet_in.end_datetime,
                         Meeting.end_datetime >= meet_in.end_datetime),
                    and_(Meeting.start_datetime >= meet_in.start_datetime,
                         Meeting.end_datetime <= meet_in.end_datetime))).distinct())

        conflicting_users = [row[0] for row in result.all()]
        if conflicting_users:
            raise HTTPException(
                status_code=400,
                detail=f"Users with IDs {conflicting_users} already have meetings at that time.")

        result = await db.execute(select(User).where(User.id.in_(participant_ids)))
        participants = result.scalars().all()

        meeting = Meeting(
            title=meet_in.title,
            description=meet_in.description,
            location=meet_in.location,
            start_datetime=meet_in.start_datetime,
            end_datetime=meet_in.end_datetime,
            creator_id=creator_id,
            participants=participants)

        db.add(meeting)
        try:
            await db.commit()
            await db.refresh(meeting)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return MeetingShortRead.model_validate(meeting)

    async def update_meet(
            self,
            db: AsyncSession,
            meeting_id: int,
            meet_in: MeetingUpdate,
            current_user_id: int
    ) -> MeetingShortRead:
        """
        Update the meeting, including adding and deleting participants,
        checking for the existence of users and time conflicts,
        and handling cancellation metadata.
        """
        result = await db.execute(
            select(Meeting)
            .options(selectinload(Meeting.participants))
            .where(Meeting.id == meeting_id)
        )
        meeting = result.scalar_one_or_none()
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")

        update_data = meet_in.model_dump(exclude={"add_participant_ids", "remove_participant_ids"}, exclude_none=True)

        new_status = update_data.get("status")
        if new_status == MeetingStatus.CANCELLED and meeting.status != MeetingStatus.CANCELLED:
            meeting.cancelled_at = datetime.now(timezone.utc)
            meeting.cancelled_by_id = current_user_id

        for field, value in update_data.items():
            setattr(meeting, field, value)

        add_ids = set(meet_in.add_participant_ids or [])
        remove_ids = set(meet_in.remove_participant_ids or [])

        all_user_ids = add_ids.union(remove_ids)
        if all_user_ids:
            result = await db.execute(select(User.id).where(User.id.in_(all_user_ids)))
            existing_user_ids = set(row[0] for row in result.all())
            missing_user_ids = all_user_ids - existing_user_ids
            if missing_user_ids:
                raise HTTPException(status_code=400, detail=f"Users with IDs {list(missing_user_ids)} do not exist.")

        if add_ids:
            result = await db.execute(select(User).where(User.id.in_(add_ids)))
            users_to_add = result.scalars().all()

            result = await db.execute(
                select(User.id)
                .join(User.meetings)
                .where(
                    User.id.in_(add_ids),
                    Meeting.status == MeetingStatus.SCHEDULED,
                    or_(
                        and_(Meeting.start_datetime <= meeting.start_datetime,
                             Meeting.end_datetime > meeting.start_datetime),
                        and_(Meeting.start_datetime < meeting.end_datetime,
                             Meeting.end_datetime >= meeting.end_datetime),
                        and_(Meeting.start_datetime >= meeting.start_datetime,
                             Meeting.end_datetime <= meeting.end_datetime))).distinct())

            conflicting_users = [row[0] for row in result.all()]
            if conflicting_users:
                raise HTTPException(
                    status_code=400,
                    detail=f"Users with IDs {conflicting_users} already have meetings at that time.")

            for user in users_to_add:
                if user not in meeting.participants:
                    meeting.participants.append(user)

        if remove_ids:
            meeting.participants = [user for user in meeting.participants if user.id not in remove_ids]

        try:
            await db.commit()
            await db.refresh(meeting)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        return MeetingShortRead.model_validate(meeting)

    async def get_by_id_detailed(self, db: AsyncSession, meeting_id: int) -> MeetingRead:
        """
        Get detailed information about the meeting by ID with
        the upload of the associated participants and creator.
        """
        result = await db.execute(
            select(Meeting)
            .options(
                selectinload(Meeting.participants),
                selectinload(Meeting.creator),
                selectinload(Meeting.cancelled_by), )
            .where(Meeting.id == meeting_id))

        meeting = result.scalar_one_or_none()
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return MeetingRead.model_validate(meeting)

    async def get_user_meetings(self, db: AsyncSession, user_id: int) -> List[MeetingShortRead]:
        """
        Get all the meetings that the specified user participates in,
        sorted by start date.
        """
        result = await db.execute(
            select(Meeting)
            .join(Meeting.participants)
            .where(User.id == user_id)
            .order_by(Meeting.start_datetime))

        meetings = result.unique().scalars().all()
        return [MeetingShortRead.model_validate(m) for m in meetings]


meeting_crud = MeetingCRUD()

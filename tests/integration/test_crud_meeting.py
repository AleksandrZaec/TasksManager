import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from src.schemas import MeetingCreate, MeetingUpdate
from src.models.enum import MeetingStatus


@pytest.mark.asyncio
class TestMeetingCRUDCreate:
    """Tests for meeting creation logic."""

    async def test_create_meet_success(self, test_session: AsyncSession, create_user, meetings_crud):
        """Create a valid meeting with one participant."""
        creator = await create_user(email="creator@example.com")
        participant = await create_user(email="participant@example.com")
        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Team sync",
            description="Weekly sync",
            location="Zoom",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[participant.id]
        )

        meeting = await meetings_crud.create_meet(test_session, meet_in, creator.id)

        assert meeting.title == "Team sync"
        assert meeting.description == "Weekly sync"
        assert meeting.location == "Zoom"
        assert meeting.start_datetime == start
        assert meeting.end_datetime == end
        assert meeting.id is not None

    async def test_create_meet_missing_user_raises(self, test_session: AsyncSession, create_user, meetings_crud):
        """Fail if a participant does not exist."""
        creator = await create_user(email="creator2@example.com")
        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Invalid meeting",
            description="Invalid user test",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[999999]
        )

        with pytest.raises(HTTPException) as exc_info:
            await meetings_crud.create_meet(test_session, meet_in, creator.id)

        assert exc_info.value.status_code == 400
        assert "do not exist" in exc_info.value.detail

    async def test_create_meet_conflicting_schedule_raises(self, test_session: AsyncSession, create_user,
                                                           meetings_crud):
        """Fail if participant has conflicting meeting."""
        creator = await create_user(email="creator3@example.com")
        participant = await create_user(email="participant2@example.com")

        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in_1 = MeetingCreate(
            title="Existing Meeting",
            description="Already scheduled",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[participant.id]
        )
        await meetings_crud.create_meet(test_session, meet_in_1, creator.id)

        meet_in_2 = MeetingCreate(
            title="Conflicting Meeting",
            description="Conflict test",
            location="Office",
            start_datetime=start + timedelta(minutes=30),
            end_datetime=end + timedelta(hours=1),
            participant_ids=[participant.id]
        )

        with pytest.raises(HTTPException) as exc_info:
            await meetings_crud.create_meet(test_session, meet_in_2, creator.id)

        assert exc_info.value.status_code == 400
        assert "already have meetings" in exc_info.value.detail


@pytest.mark.asyncio
class TestMeetingCRUDUpdate:

    async def test_update_meet(self, test_session: AsyncSession, create_user, meetings_crud):
        """Update a meeting by replacing participants."""
        creator = await create_user(email="creator4@example.com")
        participant1 = await create_user(email="participant3@example.com")
        participant2 = await create_user(email="participant4@example.com")

        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Initial Meeting",
            description="Initial desc",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[participant1.id]
        )
        meeting = await meetings_crud.create_meet(test_session, meet_in, creator.id)

        update_in = MeetingUpdate(
            title="Updated Meeting",
            description="Updated desc",
            add_participant_ids=[participant2.id],
            remove_participant_ids=[participant1.id]
        )

        updated_short = await meetings_crud.update_meet(test_session, meeting.id, update_in, current_user_id=creator.id)
        updated = await meetings_crud.get_by_id_detailed(test_session, updated_short.id)

        assert updated.title == "Updated Meeting"
        assert updated.description == "Updated desc"
        participant_ids = {p.id for p in updated.participants}
        assert participant2.id in participant_ids
        assert participant1.id not in participant_ids

    async def test_update_meet_cancel(self, test_session: AsyncSession, create_user, meetings_crud):
        """Cancel a scheduled meeting."""
        creator = await create_user(email="creator5@example.com")
        start = datetime.now(timezone.utc) + timedelta(days=3)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Cancelable Meeting",
            description="Will be cancelled",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[]
        )
        meeting = await meetings_crud.create_meet(test_session, meet_in, creator.id)

        update_in = MeetingUpdate(status=MeetingStatus.CANCELLED)

        updated_short = await meetings_crud.update_meet(test_session, meeting.id, update_in, current_user_id=creator.id)

        updated = await meetings_crud.get_by_id_detailed(test_session, updated_short.id)

        assert updated.status == MeetingStatus.CANCELLED
        assert updated.cancelled_at is not None
        assert updated.cancelled_by.id == creator.id

    async def test_update_user_raises(self, test_session: AsyncSession, create_user, meetings_crud):
        """Fail if user to add/remove is missing."""
        creator = await create_user(email="creator6@example.com")
        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Some Meeting",
            description="Desc",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[]
        )
        meeting = await meetings_crud.create_meet(test_session, meet_in, creator.id)

        update_in = MeetingUpdate(add_participant_ids=[999999])

        with pytest.raises(HTTPException) as exc_info:
            await meetings_crud.update_meet(test_session, meeting.id, update_in, current_user_id=creator.id)

        assert exc_info.value.status_code == 400
        assert "do not exist" in exc_info.value.detail

    async def test_conflicting_raises(self, test_session: AsyncSession, create_user, meetings_crud):
        """Fail if participant has conflicting time slot."""
        creator = await create_user(email="creator7@example.com")
        participant = await create_user(email="participant7@example.com")

        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in_1 = MeetingCreate(
            title="First Meeting",
            description="Desc",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[participant.id]
        )
        meeting = await meetings_crud.create_meet(test_session, meet_in_1, creator.id)

        update_in = MeetingUpdate(add_participant_ids=[participant.id])

        with pytest.raises(HTTPException) as exc_info:
            await meetings_crud.update_meet(test_session, meeting.id, update_in, current_user_id=creator.id)

        assert exc_info.value.status_code == 400
        assert "already have meetings" in exc_info.value.detail


@pytest.mark.asyncio
class TestMeetingCRUDGet:

    async def test_get_by_id(self, test_session: AsyncSession, create_user, meetings_crud):
        """Successfully retrieve a full meeting."""
        creator = await create_user(email="creator8@example.com")
        start = datetime.now(timezone.utc) + timedelta(days=1)
        end = start + timedelta(hours=1)

        meet_in = MeetingCreate(
            title="Detailed Meeting",
            description="Details",
            location="Office",
            start_datetime=start,
            end_datetime=end,
            participant_ids=[]
        )
        meeting = await meetings_crud.create_meet(test_session, meet_in, creator.id)

        detailed = await meetings_crud.get_by_id_detailed(test_session, meeting.id)

        assert detailed.id == meeting.id
        assert detailed.title == meeting.title
        assert detailed.participants is not None
        assert detailed.creator is not None

    async def test_get_by_id_not_found(self, test_session: AsyncSession, meetings_crud):
        """Fail to retrieve nonexistent meeting."""
        with pytest.raises(HTTPException) as exc_info:
            await meetings_crud.get_by_id_detailed(test_session, 999999)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestMeetingCRUDGetUserMeetings:

    async def test_get_user_meetings_empty(self, test_session: AsyncSession, create_user, meetings_crud):
        """User has no meetings."""
        user = await create_user(email="user_without_meetings@example.com")
        meetings = await meetings_crud.get_user_meetings(test_session, user.id)
        assert meetings == []

    async def test_get_user_meetings_multiple(self, test_session: AsyncSession, create_user, meetings_crud):
        """User has multiple meetings."""
        user = await create_user(email="multiuser_meetings@example.com")
        creator = await create_user(email="creator_for_meetings@example.com")

        start1 = datetime.now(timezone.utc) + timedelta(days=1)
        end1 = start1 + timedelta(hours=1)
        start2 = datetime.now(timezone.utc) + timedelta(days=2)
        end2 = start2 + timedelta(hours=2)

        meet_in_1 = MeetingCreate(
            title="Meeting One",
            description="Desc 1",
            location="Office",
            start_datetime=start1,
            end_datetime=end1,
            participant_ids=[user.id]
        )
        meet_in_2 = MeetingCreate(
            title="Meeting Two",
            description="Desc 2",
            location="Office",
            start_datetime=start2,
            end_datetime=end2,
            participant_ids=[user.id]
        )

        await meetings_crud.create_meet(test_session, meet_in_1, creator.id)
        await meetings_crud.create_meet(test_session, meet_in_2, creator.id)

        meetings = await meetings_crud.get_user_meetings(test_session, user.id)
        assert len(meetings) >= 2
        titles = {m.title for m in meetings}
        assert "Meeting One" in titles
        assert "Meeting Two" in titles

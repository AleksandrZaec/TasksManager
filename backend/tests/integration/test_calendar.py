import pytest
from datetime import datetime, timedelta, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.services.calendar import get_user_calendar, get_team_calendar
from backend.src.models import TeamRole, MeetingParticipantAssociation, Meeting
from backend.src.schemas.calendar import CalendarTask, CalendarMeeting


@pytest.mark.asyncio
class TestUserCalendar:
    async def test_user_calendar_returns_tasks_and_meetings(
            self,
            test_session: AsyncSession,
            create_user,
            create_task,
            create_team,
    ):
        """User calendar returns both tasks and meetings within date range."""
        user = await create_user(email="calendar_user@example.com")
        team = await create_team(creator_id=user.id)

        due = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
        task = await create_task(creator_id=user.id, team_id=team.id, due_date=due)

        meeting = Meeting(
            title="Daily Standup",
            start_datetime=due.replace(hour=9),
            end_datetime=due.replace(hour=9, minute=30),
            creator_id=user.id
        )
        test_session.add(meeting)
        await test_session.flush()

        assoc = MeetingParticipantAssociation(meeting_id=meeting.id, user_id=user.id)
        test_session.add(assoc)
        await test_session.commit()

        start = date.today()
        end = start + timedelta(days=3)

        calendar = await get_user_calendar(test_session, start, end, user.id)

        assert due.date() in calendar
        event_titles = [e.title for e in calendar[due.date()]]
        assert "Daily Standup" in event_titles
        assert any(isinstance(e, CalendarTask) for e in calendar[due.date()])
        assert any(isinstance(e, CalendarMeeting) for e in calendar[due.date()])


@pytest.mark.asyncio
class TestTeamCalendar:
    async def test_team_calendar_returns_tasks_and_meetings(
            self,
            test_session: AsyncSession,
            create_user,
            create_task,
            create_team,
    ):
        """Team calendar returns both tasks and meetings within date range."""
        creator = await create_user(email="team_creator@example.com")
        team = await create_team(creator_id=creator.id)

        user = await create_user(email="team_member@example.com")

        from backend.src.models import TeamUserAssociation
        team_user = TeamUserAssociation(team_id=team.id, user_id=user.id, role=TeamRole.EXECUTOR)
        test_session.add(team_user)

        due = datetime.now(timezone.utc).replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
        task = await create_task(creator_id=creator.id, team_id=team.id, due_date=due)

        meeting = Meeting(
            title="Team Sync",
            start_datetime=due.replace(hour=14),
            end_datetime=due.replace(hour=14, minute=45),
            creator_id=creator.id
        )
        test_session.add(meeting)
        await test_session.flush()

        assoc = MeetingParticipantAssociation(meeting_id=meeting.id, user_id=user.id)
        test_session.add(assoc)
        await test_session.commit()

        start = date.today()
        end = start + timedelta(days=3)

        calendar = await get_team_calendar(test_session, team.id, start, end)

        assert due.date() in calendar
        event_titles = [e.title for e in calendar[due.date()]]
        assert "Team Sync" in event_titles
        assert any(isinstance(e, CalendarTask) for e in calendar[due.date()])
        assert any(isinstance(e, CalendarMeeting) for e in calendar[due.date()])

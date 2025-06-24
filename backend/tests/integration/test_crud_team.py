import pytest
from fastapi import HTTPException
from sqlalchemy import select
from backend.src.models import TeamRole, TeamUserAssociation
from backend.src.schemas import TeamCreate, TeamUpdate, TeamUserAdd


@pytest.mark.asyncio
class TestTeamCRUDCreate:

    async def test_create_team_success(self, test_session, create_user, teams_crud):
        """Test successful creation of a team without users."""
        creator = await create_user(email="creator@example.com")
        team_in = TeamCreate(name="New Team", description="Description", users=[])

        team = await teams_crud.create_team(test_session, team_in, creator_id=creator.id)

        assert team.name == "New Team"
        assert team.description == "Description"
        assert hasattr(team, "id")

    async def test_create_team_duplicate_name(self, test_session, create_user, teams_crud):
        """Test creation fails when team name already exists."""
        creator = await create_user(email="creator2@example.com")
        team_in = TeamCreate(name="Dup Team", description="Desc", users=[])

        await teams_crud.create_team(test_session, team_in, creator_id=creator.id)

        with pytest.raises(HTTPException) as exc_info:
            await teams_crud.create_team(test_session, team_in, creator_id=creator.id)

        assert exc_info.value.status_code == 400
        assert "Team with this name already exists" in exc_info.value.detail

    async def test_create_team_with_users_success(self, test_session, create_user, teams_crud):
        """Test successful creation of a team with multiple users."""
        creator = await create_user(email="creator3@example.com")
        user1 = await create_user(email="member1@example.com")
        user2 = await create_user(email="member2@example.com")

        users = [
            TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value),
            TeamUserAdd(user_id=user2.id, role=TeamRole.MANAGER.value),
        ]

        team_in = TeamCreate(name="TeamWithUsers", description="Desc", users=users)

        team = await teams_crud.create_team(test_session, team_in, creator_id=creator.id)

        assert team.name == "TeamWithUsers"

        stmt = select(TeamUserAssociation).where(TeamUserAssociation.team_id == team.id)
        result = await test_session.execute(stmt)
        associations = result.scalars().all()
        user_ids = {assoc.user_id for assoc in associations}
        assert creator.id in user_ids
        assert user1.id in user_ids
        assert user2.id in user_ids


@pytest.mark.asyncio
class TestTeamCRUDUpdate:

    async def test_update_team_success(self, test_session, create_user, create_team, teams_crud):
        """Test successful update of team details."""
        creator = await create_user(email="creator_update@example.com")
        team = await create_team(name="OldName", creator_id=creator.id)

        team_in = TeamUpdate(name="Updated Name", description="Updated desc")

        updated = await teams_crud.update_team(test_session, team.id, team_in)

        assert updated.name == "Updated Name"
        assert updated.description == "Updated desc"

    async def test_update_team_not_found(self, test_session, teams_crud):
        """Test update fails when team does not exist."""
        team_in = TeamUpdate(name="NoTeam")
        with pytest.raises(HTTPException) as exc_info:
            await teams_crud.update_team(test_session, 999999, team_in)
        assert exc_info.value.status_code == 404

    async def test_update_team_duplicate_name(self, test_session, create_user, create_team, teams_crud):
        """Test update fails when new name duplicates an existing team."""
        creator = await create_user(email="creator_dup@example.com")
        team1 = await create_team(name="Team1", creator_id=creator.id)
        team2 = await create_team(name="Team2", creator_id=creator.id)

        team_in = TeamUpdate(name="Team1")
        with pytest.raises(HTTPException) as exc_info:
            await teams_crud.update_team(test_session, team2.id, team_in)

        assert exc_info.value.status_code == 400
        assert "Team name already exists" in exc_info.value.detail


@pytest.mark.asyncio
class TestTeamCRUDGetByIdWithRelations:

    async def test_get_team_with_relations_success(self, test_session, create_user, create_team, teams_crud):
        """Test retrieval of a team with users and tasks."""
        creator = await create_user(email="creator_rel@example.com")
        team = await create_team(name="RelTeam", creator_id=creator.id)

        user = await create_user(email="member_rel@example.com")
        assoc = TeamUserAssociation(team_id=team.id, user_id=user.id, role=TeamRole.EXECUTOR)
        test_session.add(assoc)
        await test_session.commit()

        result = await teams_crud.get_by_id_with_relations(test_session, team.id)

        assert result.id == team.id
        assert any(u.user_id == user.id for u in result.team_users)
        assert isinstance(result.tasks, list)

    async def test_get_team_not_found(self, test_session, teams_crud):
        """Test 404 is raised when team not found."""
        with pytest.raises(HTTPException) as exc_info:
            await teams_crud.get_by_id_with_relations(test_session, 999999)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestTeamCRUDGetUserTeams:

    async def test_get_user_teams_empty(self, test_session, create_user, teams_crud):
        """Test returns empty list if user belongs to no teams."""
        user = await create_user(email="emptyuser@example.com")
        teams = await teams_crud.get_user_teams(test_session, user.id)
        assert teams == []

    async def test_get_user_teams_multiple(self, test_session, create_user, create_team, teams_crud):
        """Test returns multiple teams user belongs to."""
        user = await create_user(email="multiuser@example.com")
        team1 = await create_team(name="UserTeam1", creator_id=user.id)
        team2 = await create_team(name="UserTeam2", creator_id=user.id)

        teams = await teams_crud.get_user_teams(test_session, user.id)

        names = {team.name for team in teams}
        assert "UserTeam1" in names
        assert "UserTeam2" in names

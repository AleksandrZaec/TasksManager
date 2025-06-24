import pytest
from fastapi import HTTPException
from backend.src.models import TeamRole
from backend.src.schemas import TeamUserAdd


@pytest.mark.asyncio
class TestTeamUserCRUDAddUsers:
    """Tests for adding users to a team."""

    async def test_add_users_success(self, test_session, create_user, create_team, team_users_crud):
        """Add multiple new users to a team successfully."""
        creator = await create_user(email="creator@example.com")
        team = await create_team(name="AddUsersTeam", creator_id=creator.id)

        user1 = await create_user(email="user1@example.com")
        user2 = await create_user(email="user2@example.com")

        users = [
            TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value),
            TeamUserAdd(user_id=user2.id, role=TeamRole.MANAGER.value),
        ]

        response = await team_users_crud.add_users(test_session, team.id, users)

        added_ids = [user.id for user in response.added]
        assert user1.id in added_ids
        assert user2.id in added_ids
        assert response.errors == []

    async def test_add_users_some_already_members(self, test_session, create_user, create_team, team_users_crud):
        """Adding users when some are already members returns errors for those."""
        creator = await create_user(email="creator2@example.com")
        team = await create_team(name="ExistingMembersTeam", creator_id=creator.id)

        user1 = await create_user(email="user1@example.com")
        user2 = await create_user(email="user2@example.com")

        # Add user1 initially
        await team_users_crud.add_users(test_session, team.id, [TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value)])

        # Try adding both users again
        users = [
            TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value),
            TeamUserAdd(user_id=user2.id, role=TeamRole.MANAGER.value),
        ]

        response = await team_users_crud.add_users(test_session, team.id, users)

        added_ids = [user.id for user in response.added]
        assert user2.id in added_ids
        assert user1.id not in added_ids
        assert any(f"user with id {user1.id} is already a member" in err.lower() for err in response.errors)

    async def test_add_users_no_users_provided(self, team_users_crud, test_session):
        """Adding users with empty list raises HTTP 400."""
        with pytest.raises(HTTPException) as exc_info:
            await team_users_crud.add_users(test_session, team_id=1, users=[])
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
class TestTeamUserCRUDRemoveUsers:
    """Tests for removing users from a team."""

    async def test_remove_users_success(self, test_session, create_user, create_team, team_users_crud):
        """Remove existing users from a team successfully."""
        creator = await create_user(email="creator_rem@example.com")
        team = await create_team(name="RemoveUsersTeam", creator_id=creator.id)

        user1 = await create_user(email="user1@example.com")
        user2 = await create_user(email="user2@example.com")

        await team_users_crud.add_users(test_session, team.id, [
            TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value),
            TeamUserAdd(user_id=user2.id, role=TeamRole.MANAGER.value),
        ])

        response = await team_users_crud.remove_users(test_session, team.id, [user1.id, user2.id])

        assert set(response.removed) == {user1.id, user2.id}
        assert response.not_found == []

    async def test_remove_users_some_not_found(self, test_session, create_user, create_team, team_users_crud):
        """Remove users where some user IDs are not in the team."""
        creator = await create_user(email="creator_rem2@example.com")
        team = await create_team(name="RemoveUsersTeam2", creator_id=creator.id)

        user1 = await create_user(email="user1@example.com")

        await team_users_crud.add_users(test_session, team.id, [
            TeamUserAdd(user_id=user1.id, role=TeamRole.EXECUTOR.value),
        ])

        fake_user_id = 999999

        response = await team_users_crud.remove_users(test_session, team.id, [user1.id, fake_user_id])

        assert user1.id in response.removed
        assert fake_user_id in response.not_found

    async def test_remove_users_no_ids_provided(self, team_users_crud, test_session):
        """Removing users with empty list raises HTTP 400."""
        with pytest.raises(HTTPException) as exc_info:
            await team_users_crud.remove_users(test_session, team_id=1, user_ids=[])
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
class TestTeamUserCRUDUpdateUserRole:
    """Tests for updating user role in a team."""

    async def test_update_user_role_success(self, test_session, create_user, create_team, team_users_crud):
        """Successfully update role of existing team user."""
        creator = await create_user(email="creator_role@example.com")
        team = await create_team(name="UpdateRoleTeam", creator_id=creator.id)

        user = await create_user(email="user@example.com")

        await team_users_crud.add_users(test_session, team.id, [
            TeamUserAdd(user_id=user.id, role=TeamRole.EXECUTOR.value),
        ])

        response = await team_users_crud.update_user_role(test_session, team.id, user.id, TeamRole.MANAGER)

        assert response == {"msg": "User role updated"}

    async def test_update_user_role_user_not_in_team(self, test_session, create_user, create_team, team_users_crud):
        """Updating role fails if user is not a member of the team."""
        creator = await create_user(email="creator_role2@example.com")
        team = await create_team(name="UpdateRoleTeam2", creator_id=creator.id)

        user = await create_user(email="user2@example.com")

        with pytest.raises(HTTPException) as exc_info:
            await team_users_crud.update_user_role(test_session, team.id, user.id, TeamRole.MANAGER)

        assert exc_info.value.status_code == 404


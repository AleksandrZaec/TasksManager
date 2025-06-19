from typing import List
from backend.src.models import User, TeamUserAssociation, TeamRole
from backend.src.schemas import AddUsersResponse, UsersRemoveResponse, TeamUserAssociationRead, TeamUserAdd, \
    AddedUserInfo
from backend.src.services.basecrud import BaseCRUD
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import aliased


class TeamUserCRUD(BaseCRUD):
    """CRUD operations for team-user associations."""

    def __init__(self):
        super().__init__(TeamUserAssociation, TeamUserAssociationRead)

    async def add_users(self, db: AsyncSession, team_id: int, users: List[TeamUserAdd]) -> AddUsersResponse:
        """Add multiple users to a team with roles."""
        if not users:
            raise HTTPException(status_code=400, detail="No users provided for addition")

        user_ids = [u.user_id for u in users]
        errors = []
        added = []

        U = aliased(User)
        TUA = aliased(TeamUserAssociation)

        stmt = (
            select(U.id, U.email, U.first_name, U.last_name, TUA.user_id.label("assoc_user_id"))
            .outerjoin(TUA, (TUA.user_id == U.id) & (TUA.team_id == team_id))
            .where(U.id.in_(user_ids)))
        result = await db.execute(stmt)
        rows = result.all()

        user_data_map = {}
        for user_id, email, first_name, last_name, assoc_user_id in rows:
            user_data_map[user_id] = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "in_team": assoc_user_id is not None
            }

        new_assocs = []

        for user in users:
            data = user_data_map.get(user.user_id)
            if data is None:
                errors.append(f"User with id {user.user_id} not found")
                continue
            if data["in_team"]:
                errors.append(f"User with id {user.user_id} is already a member of the team")
                continue

            new_assocs.append(
                TeamUserAssociation(
                    team_id=team_id,
                    user_id=user.user_id,
                    role=user.role))
            added.append(
                AddedUserInfo(
                    id=user.user_id,
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"]))

        if not new_assocs:
            raise HTTPException(status_code=400, detail="No new users to add or all users already members")

        db.add_all(new_assocs)

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return AddUsersResponse(added=added, errors=errors)

    async def remove_users(self, db: AsyncSession, team_id: int, user_ids: List[int]) -> UsersRemoveResponse:
        """Remove multiple users from a team by their IDs."""

        if not user_ids:
            raise HTTPException(status_code=400, detail="No user IDs provided for removal")

        stmt = (
            delete(TeamUserAssociation)
            .where(
                TeamUserAssociation.team_id == team_id,
                TeamUserAssociation.user_id.in_(user_ids))
            .returning(TeamUserAssociation.user_id))

        result = await db.execute(stmt)
        removed_user_ids = [user_id for (user_id,) in result.all()]

        await db.commit()

        not_found = list(set(user_ids) - set(removed_user_ids))

        return UsersRemoveResponse(
            removed=removed_user_ids,
            not_found=not_found)

    async def update_user_role(self, db: AsyncSession, team_id: int, user_id: int, role: TeamRole) -> dict:
        """Update a user's role inside a team. Raise if not found."""
        stmt = (update(TeamUserAssociation).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id == user_id
        ).values(role=role).execution_options(synchronize_session="fetch"))

        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of the team")

        return {"msg": "User role updated"}


team_users_crud = TeamUserCRUD()

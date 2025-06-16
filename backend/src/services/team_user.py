from backend.src.models import User
from backend.src.services.basecrud import BaseCRUD
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models.association import TeamUserAssociation, TeamRole
from backend.src.schemas.team_user import TeamUserAssociationRead
from sqlalchemy import select, delete, update


class TeamUserCRUD(BaseCRUD):
    """CRUD operations for team-user associations."""

    def __init__(self):
        super().__init__(TeamUserAssociation, TeamUserAssociationRead)

    async def add_user(self, db: AsyncSession, team_id: int, email: str, role: TeamRole = TeamRole.EXECUTOR) -> dict:
        """Add a user to a team with a specific role. Raise if already exists."""
        stmt = select(User.id).where(User.email == email)
        result = await db.execute(stmt)
        user_id = result.scalar_one_or_none()

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )

        stmt = select(TeamUserAssociation).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id == user_id)

        result = await db.execute(stmt)
        existing_assoc = result.scalar_one_or_none()

        if existing_assoc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of the team"
            )

        new_assoc = TeamUserAssociation(
            team_id=team_id,
            user_id=user_id,
            role=role
        )
        db.add(new_assoc)
        await db.commit()

        return {"msg": "User added to team"}

    async def remove_user(self, db: AsyncSession, team_id: int, user_id: int) -> None:
        """Remove a user from a team."""
        stmt = delete(TeamUserAssociation).where(
            TeamUserAssociation.team_id == team_id,
            TeamUserAssociation.user_id == user_id)

        await db.execute(stmt)
        await db.commit()
        return None

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

# async def add_users_bulk(self, db: AsyncSession, team_id: int, user_emails: list[str]) -> dict:
#     """Add users to a team by email. All will get default role. Skip already existing ones."""
#
#     if not user_emails:
#         return {"msg": "No emails provided", "added": 0, "skipped": 0}
#
#     stmt = select(User.id, User.email).where(User.email.in_(user_emails))
#     result = await db.execute(stmt)
#     users = result.all()  # list of (id, email)
#
#     email_to_id = {email: uid for uid, email in users}
#     found_emails = set(email_to_id.keys())
#
#     missing_emails = set(user_emails) - found_emails
#     if missing_emails:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Users with these emails not found: {', '.join(missing_emails)}"
#         )
#
#     user_ids = list(email_to_id.values())
#
#     stmt = select(TeamUserAssociation.user_id).where(
#         TeamUserAssociation.team_id == team_id,
#         TeamUserAssociation.user_id.in_(user_ids)
#     )
#     result = await db.execute(stmt)
#     existing_user_ids = {row[0] for row in result.all()}
#
#     new_user_ids = [uid for uid in user_ids if uid not in existing_user_ids]
#
#     if new_user_ids:
#         stmt = insert(TeamUserAssociation).values([
#             {"team_id": team_id, "user_id": uid} for uid in new_user_ids
#         ])
#         await db.execute(stmt)
#         await db.commit()
#
#     return {
#         "msg": f"{len(new_user_ids)} users added",
#         "added": len(new_user_ids),
#         "skipped": len(user_ids) - len(new_user_ids)
#     }
#
# async def remove_users_bulk(self, db: AsyncSession, team_id: int, user_ids: list[int]) -> dict:
#     """Remove a users from a team. No error if user not found."""
#     if not user_ids:
#         return {"msg": "No user IDs provided", "deleted": 0}
#
#     stmt = delete(TeamUserAssociation).where(
#         TeamUserAssociation.team_id == team_id,
#         TeamUserAssociation.user_id.in_(user_ids))
#
#     result = await db.execute(stmt)
#     await db.commit()
#
#     return {"msg": f"{result.rowcount} users removed from team", "deleted": result.rowcount}


from fastapi import Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Type, Any, Callable
from src.config.db import get_db
from src.models import UserRole, TaskAssigneeAssociation, User
from src.schemas.user import UserPayload, TeamRole
from src.services.auth import get_current_user


async def is_admin(current_user: UserPayload = Depends(get_current_user)) -> UserPayload:
    """Allow access only for users with ADMIN role."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint")
    return current_user


async def is_team_member(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are members of the team specified by `team_id` path param."""
    if team_id not in [team.team_id for team in current_user.teams]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this team.")
    return current_user


async def is_admin_and_member(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are admins and members of the specified team."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint")
    if team_id not in [team.team_id for team in current_user.teams]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this team")
    return current_user


async def admin_manager_in_team(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for admins or users who are MANAGER in the specified team."""
    team_assoc = next((team for team in current_user.teams if team.team_id == team_id), None)
    if not team_assoc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this team.")
    if current_user.role == UserRole.ADMIN.value:
        return current_user
    if team_assoc.role != TeamRole.MANAGER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You must be a manager in this team.")
    return current_user


async def admin_or_manager(
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are admins or managers in any of their teams."""
    if current_user.role == UserRole.ADMIN.value:
        return current_user
    if any(team.role == TeamRole.MANAGER for team in current_user.teams):
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only admins or team managers can access this endpoint.")


async def can_change_status(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(get_current_user),
) -> UserPayload:
    """Allow changing task status for admins, managers of the team, or assignees of the task."""
    team_assoc = next((team for team in current_user.teams if team.team_id == team_id), None)
    if not team_assoc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this team.")
    if current_user.role == UserRole.ADMIN.value:
        return current_user
    if team_assoc.role == TeamRole.MANAGER:
        return current_user
    stmt = select(TaskAssigneeAssociation.user_id).where(TaskAssigneeAssociation.task_id == task_id)
    result = await db.execute(stmt)
    assignee_ids = [row[0] for row in result.all()]
    if current_user.id in assignee_ids:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not allowed to change the task status.")


async def block_everyone() -> None:
    """Deny access to everyone - endpoint disabled."""
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This endpoint is disabled")


def creator_or_superuser(
        model: Type[Any],
        id_path_param: str = "id",
        creator_field: str = "creator_id"
) -> Callable:
    """Allow access if current user is creator of the resource or a superuser."""

    async def verify(
            resource_id: int = Path(..., alias=id_path_param, description=f"ID of the {model.__name__.lower()}"),
            db: AsyncSession = Depends(get_db),
            current_user: UserPayload = Depends(get_current_user),
    ) -> UserPayload:
        stmt = select(model).where(getattr(model, "id") == resource_id)
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()

        if not resource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")

        if getattr(resource, creator_field) == current_user.id:
            return current_user

        user_stmt = select(User.is_superuser).where(User.id == current_user.id)
        user_result = await db.execute(user_stmt)
        is_superuser = user_result.scalar_one_or_none()

        if is_superuser:
            return current_user

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You do not have permission to modify this {model.__name__.lower()}.")

    return verify


def creator_only(
        model: Type[Any],
        id_path_param: str = "id",
        creator_field: str = "creator_id"
) -> Callable:
    """Allow access only if current user is the creator of the resource."""

    async def verify(
            resource_id: int = Path(..., alias=id_path_param, description=f"ID of the {model.__name__.lower()}"),
            db: AsyncSession = Depends(get_db),
            current_user: UserPayload = Depends(get_current_user),
    ) -> UserPayload:
        stmt = select(model).where(getattr(model, "id") == resource_id)
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")

        if getattr(resource, creator_field) != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only the creator can perform this action")

        return current_user

    return verify

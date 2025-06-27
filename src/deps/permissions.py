from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Type, Any, Callable
from src.config.db import get_db
from src.models import UserRole, TaskAssigneeAssociation
from src.schemas.user import UserPayload
from src.services.auth import get_current_user
from src.utils.permissions import is_member_of_team
from src.constants import (
    ERROR_NOT_TEAM_MEMBER,
    ERROR_ONLY_ADMIN,
    ERROR_ONLY_MANAGER,
    ERROR_ADMIN_OR_MANAGER_REQUIRED,
    ERROR_TASK_STATUS_PERMISSION,
    ERROR_ENDPOINT_DISABLED,
    ERROR_ONLY_CREATOR,
)


async def is_admin(current_user: UserPayload = Depends(get_current_user)) -> UserPayload:
    """Allow access only for users with ADMIN role."""
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ONLY_ADMIN)
    return current_user


async def is_team_member(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are members of the team specified by `team_id` path param."""
    if not is_member_of_team(current_user, team_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_NOT_TEAM_MEMBER)
    return current_user


async def is_admin_and_member(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are admins and members of the specified team."""
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ONLY_ADMIN)
    if not is_member_of_team(current_user, team_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_NOT_TEAM_MEMBER)
    return current_user


async def admin_manager_in_team(
        team_id: int = Path(..., description="ID of the team"),
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for admins or users who are MANAGER in the specified team."""
    from src.schemas.user import TeamRole

    team_assoc = next((team for team in current_user.teams if team.team_id == team_id), None)
    if not team_assoc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_NOT_TEAM_MEMBER)
    if UserRole(current_user.role) == UserRole.ADMIN:
        return current_user
    if not team_assoc or team_assoc.role != TeamRole.MANAGER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ONLY_MANAGER)
    return current_user


async def admin_or_manager(
        current_user: UserPayload = Depends(get_current_user)
) -> UserPayload:
    """Allow access only for users who are admins or managers in any of their teams."""
    from src.schemas.user import TeamRole

    if UserRole(current_user.role) == UserRole.ADMIN:
        return current_user
    if any(team.role == TeamRole.MANAGER for team in current_user.teams):
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ADMIN_OR_MANAGER_REQUIRED)


async def can_change_status(
        team_id: int = Path(..., description="ID of the team"),
        task_id: int = Path(..., description="ID of the task"),
        db: AsyncSession = Depends(get_db),
        current_user: UserPayload = Depends(get_current_user),
) -> UserPayload:
    """Allow changing task status for admins, managers of the team, or assignees of the task."""
    from src.schemas.user import TeamRole

    team_assoc = next((team for team in current_user.teams if team.team_id == team_id), None)
    if not team_assoc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_NOT_TEAM_MEMBER)
    if UserRole(current_user.role) == UserRole.ADMIN or team_assoc.role == TeamRole.MANAGER:
        return current_user
    stmt = select(TaskAssigneeAssociation.user_id).where(TaskAssigneeAssociation.task_id == task_id)
    result = await db.execute(stmt)

    assignee_ids = [user_id for (user_id,) in result.all()]

    if current_user.id in assignee_ids:
        return current_user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_TASK_STATUS_PERMISSION)


async def block_everyone() -> None:
    """Deny access to everyone - endpoint disabled."""
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ENDPOINT_DISABLED)


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

        if not hasattr(model, "id"):
            raise ValueError(f"{model.__name__} must have an 'id' field")

        stmt = select(model).where(getattr(model, "id") == resource_id)
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()

        if not resource:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
        if getattr(resource, creator_field) == current_user.id:
            return current_user
        if current_user.is_superuser:
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
        if not hasattr(model, "id"):
            raise ValueError(f"{model.__name__} must have an 'id' field")

        stmt = select(model).where(getattr(model, "id") == resource_id)
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
        if getattr(resource, creator_field) != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_ONLY_CREATOR)

        return current_user

    return verify

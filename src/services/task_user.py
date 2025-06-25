from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from fastapi import HTTPException, status
from src.models import TaskAssigneeAssociation, User
from src.schemas import TaskUserAdd, AddUsersResponse, AddedUserInfo, \
    UsersRemoveResponse, RoleUpdatePayload, RoleUpdateResponse
from src.services.basecrud import BaseCRUD
from sqlalchemy.orm import aliased


class TaskAssigneeCRUD(BaseCRUD):
    """CRUD operations for TaskAssigneeAssociation model."""

    def __init__(self):
        super().__init__(TaskAssigneeAssociation, AddUsersResponse)

    async def add_executors(self, db: AsyncSession, task_id: int, obj_in: List[TaskUserAdd]) -> AddUsersResponse:
        """Add users as executors to a task by their IDs with optional roles."""
        if not obj_in:
            raise HTTPException(status_code=400, detail="No users provided to add")

        user_ids = [assignee.user_id for assignee in obj_in]
        errors = []
        added = []

        U = aliased(User)
        TAA = aliased(TaskAssigneeAssociation)

        stmt = (
            select(U.id, U.email, U.first_name, U.last_name, TAA.user_id.label("assoc_user_id"))
            .outerjoin(TAA, (TAA.user_id == U.id) & (TAA.task_id == task_id))
            .where(U.id.in_(user_ids)))

        result = await db.execute(stmt)
        rows = result.all()

        user_data_map = {
            user_id: {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "assigned": assoc_user_id is not None
            }
            for user_id, email, first_name, last_name, assoc_user_id in rows
        }

        new_assocs = []

        for assignee in obj_in:
            data = user_data_map.get(assignee.user_id)
            if data is None:
                errors.append(f"User with id {assignee.user_id} not found")
                continue
            if data["assigned"]:
                errors.append(f"User with id {assignee.user_id} is already assigned to the task")
                continue

            new_assocs.append(
                TaskAssigneeAssociation(
                    task_id=task_id,
                    user_id=assignee.user_id,
                    role=assignee.role or "executor"))
            added.append(
                AddedUserInfo(
                    id=assignee.user_id,
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"]))

        if new_assocs:
            db.add_all(new_assocs)
            try:
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return AddUsersResponse(added=added, errors=errors)

    async def remove_executors(self, db: AsyncSession, task_id: int, user_ids: List[int]) -> UsersRemoveResponse:
        """Remove multiple users as executors from a task by their IDs."""
        if not user_ids:
            raise HTTPException(status_code=400, detail="No user IDs provided for removal")

        stmt = (
            delete(TaskAssigneeAssociation)
            .where(
                TaskAssigneeAssociation.task_id == task_id,
                TaskAssigneeAssociation.user_id.in_(user_ids))
            .returning(TaskAssigneeAssociation.user_id))

        result = await db.execute(stmt)
        deleted_user_ids = [user_id for (user_id,) in result.all()]

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        not_found = sorted(set(user_ids) - set(deleted_user_ids))

        return UsersRemoveResponse(
            removed=deleted_user_ids,
            not_found=not_found)

    async def update_executor_role(
            self, db: AsyncSession,
            task_id: int, user_id: int,
            payload: RoleUpdatePayload
    ) -> RoleUpdateResponse:
        """Update the role of an executor assigned to a task."""
        stmt = (
            update(TaskAssigneeAssociation)
            .where(
                TaskAssigneeAssociation.task_id == task_id,
                TaskAssigneeAssociation.user_id == user_id, )
            .values(role=payload.new_role)
            .execution_options(synchronize_session="fetch"))

        result = await db.execute(stmt)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Executor not found for this task")

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {e}")

        return RoleUpdateResponse(msg="Role updated")


task_user_crud = TaskAssigneeCRUD()

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from fastapi import HTTPException, status
from backend.src.models import TaskAssigneeAssociation, User
from backend.src.schemas.task_user import TaskAssigneeRead, TaskUserAdd
from backend.src.services.basecrud import BaseCRUD


class TaskAssigneeCRUD(BaseCRUD):
    """CRUD operations for TaskAssigneeAssociation model."""

    def __init__(self):
        super().__init__(TaskAssigneeAssociation, TaskAssigneeRead)

    async def add_executors(self, db: AsyncSession, task_id: int, obj_in: List[TaskUserAdd]) -> dict:
        """Add users as executors to a task by their emails with optional roles."""
        emails = [user.email for user in obj_in]

        stmt = select(User.id, User.email).where(User.email.in_(emails))
        result = await db.execute(stmt)
        user_map = {email: user_id for user_id, email in result.all()}

        stmt = select(TaskAssigneeAssociation.user_id).where(TaskAssigneeAssociation.task_id == task_id)
        result = await db.execute(stmt)
        existing_user_ids = set(result.scalars().all())

        new_assocs = []
        added_emails = []
        errors = []

        for assignee in obj_in:
            user_id = user_map.get(assignee.email)
            if not user_id:
                errors.append(f"User with email {assignee.email} not found")
                continue
            if user_id in existing_user_ids:
                errors.append(f"User {assignee.email} is already assigned to the task")
                continue

            assoc = TaskAssigneeAssociation(
                task_id=task_id,
                user_id=user_id,
                role=assignee.role or "executor"
            )
            new_assocs.append(assoc)
            added_emails.append(assignee.email)

        if not new_assocs:
            raise HTTPException(status_code=400, detail="No new users to add or all users already assigned")

        db.add_all(new_assocs)
        await db.commit()

        return {"added": added_emails, "errors": errors}

    async def remove_executor(self, db: AsyncSession, task_id: int, user_id: int) -> None:
        """Remove a user as an executor from a task."""
        stmt = delete(TaskAssigneeAssociation).where(
            TaskAssigneeAssociation.task_id == task_id,
            TaskAssigneeAssociation.user_id == user_id)

        await db.execute(stmt)
        await db.commit()
        return None

    async def update_executor_role(self, db: AsyncSession, task_id: int, user_id: int, new_role: str) -> dict:
        """Update the role of an executor in a task."""
        stmt = (
            update(TaskAssigneeAssociation)
            .where(
                TaskAssigneeAssociation.task_id == task_id,
                TaskAssigneeAssociation.user_id == user_id,
            )
            .values(role=new_role)
            .execution_options(synchronize_session="fetch"))

        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Executor not found for this task")

        return {"msg": "Role updated"}


task_user_crud = TaskAssigneeCRUD()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from fastapi import HTTPException, status
from backend.src.models.association import TaskAssigneeAssociation
from backend.src.schemas.task_user import TaskAssigneeCreate, TaskAssigneeRead
from backend.src.services.basecrud import BaseCRUD


class TaskAssigneeCRUD(BaseCRUD):
    """CRUD operations for TaskAssigneeAssociation model."""

    def __init__(self):
        super().__init__(TaskAssigneeAssociation, TaskAssigneeRead)

    async def add_executor(self, db: AsyncSession, task_id: int, obj_in: TaskAssigneeCreate) -> dict:
        """Add a user as an executor to a task."""
        stmt = select(TaskAssigneeAssociation).where(
            TaskAssigneeAssociation.task_id == task_id,
            TaskAssigneeAssociation.user_id == obj_in.user_id
        )

        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already assigned to this task"
            )

        assoc = TaskAssigneeAssociation(
            task_id=task_id,
            user_id=obj_in.user_id,
            role=obj_in.role,
        )

        db.add(assoc)
        await db.commit()

        return {"msg": "Executor is appointed"}

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

from backend.src.models.task import Task
from backend.src.services.basecrud import BaseCRUD
from backend.src.schemas.task import TaskRead, TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from backend.src.models.enum import TaskStatus


class TaskCRUD(BaseCRUD):
    def __init__(self):
        """Init with Task model and TaskRead schema."""
        super().__init__(Task, TaskRead)

    class TaskCRUD:
        async def create(self, db: AsyncSession, obj_in: TaskCreate, creator_id: int, team_id: int) -> TaskRead:
            """Create a new task with given creator and team."""
            data = obj_in.model_dump()
            data["creator_id"] = creator_id
            data["team_id"] = team_id

            task = Task(**data)
            db.add(task)
            await db.commit()
            await db.refresh(task)

            return TaskRead.model_validate(task)

        async def update(self, db: AsyncSession, obj_id: int, obj_in: TaskUpdate) -> TaskRead:
            """Update task fields with new values."""
            result = await db.execute(select(Task).where(Task.id == obj_id))
            task = result.scalar_one_or_none()
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            db.add(task)
            await db.commit()
            await db.refresh(task)

            return TaskRead.model_validate(task)

        async def update_status(self, db: AsyncSession, task_id: int, new_status: TaskStatus) -> TaskRead:
            """Update only the status field of a task."""
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            task.status = new_status
            db.add(task)
            await db.commit()
            await db.refresh(task)

            return TaskRead.model_validate(task)


task_crud = TaskCRUD()


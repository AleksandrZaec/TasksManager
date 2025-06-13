from backend.models.task import Task
from backend.crud.basecrud import BaseCRUD
from backend.schemas.task import TaskRead, TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from backend.models.enum import TaskStatus


class TaskCRUD(BaseCRUD):
    def __init__(self):
        """Init with Task model and TaskRead schema."""
        super().__init__(Task, TaskRead)

    async def create(self, db: AsyncSession, obj_in: TaskCreate, creator_id: int, team_id: int) -> TaskRead:
        """Create a new task with given creator and team."""
        data = obj_in.model_dump()
        data["creator_id"] = creator_id
        data["team_id"] = team_id
        task = self.model(**data)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return TaskRead.model_validate(task)

    async def update(self, db: AsyncSession, obj_id: int, obj_in: TaskUpdate) -> TaskRead:
        """Update task fields with new values."""
        result = await db.execute(select(Task).where(Task.id == obj_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Task not found")

        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(obj, field, value)

        await db.commit()
        await db.refresh(obj)
        return TaskRead.model_validate(obj)

    async def update_status(self, db: AsyncSession, task_id: int, new_status: TaskStatus) -> TaskRead:
        """Update only the status field of a task."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Task not found")

        obj.status = new_status
        await db.commit()
        await db.refresh(obj)
        return TaskRead.model_validate(obj)


task_crud = TaskCRUD()

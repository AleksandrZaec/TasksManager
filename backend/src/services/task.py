from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from backend.src.models import Task, TaskStatus, TaskPriority, User
from backend.src.models.task_status_history import TaskStatusHistory
from backend.src.schemas.task import TaskRead, TaskShortRead, TaskCreate
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy.orm import selectinload


class TaskCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(model=Task, read_schema=TaskRead)

    async def create(self, db: AsyncSession, task_in: TaskCreate, creator_id: int, team_id: int) -> TaskShortRead:
        """Create a new task with the given input, creator, and team."""
        data = task_in.model_dump()
        data["creator_id"] = creator_id
        data["team_id"] = team_id

        task = Task(**data)
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return TaskShortRead.model_validate(task)

    async def get_all(self, db: AsyncSession) -> List[TaskShortRead]:
        """Retrieve all tasks from the database."""
        result = await db.execute(select(Task))
        tasks = result.scalars().all()
        return [TaskShortRead.model_validate(task) for task in tasks]

    async def get_by_id(self, db: AsyncSession, task_id: int) -> TaskRead:
        """Retrieve a task by ID with its creator and assignees preloaded."""
        result = await db.execute(
            select(Task).options(
                selectinload(Task.creator), selectinload(Task.assignees))
            .where(Task.id == task_id))

        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "creator_email": task.creator.email if task.creator else None,
            "assignees": [user.email for user in task.assignees],
            "team_id": task.team_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }

        return TaskRead(**task_data)

    async def update_status(
            self,
            db: AsyncSession,
            task_id: int,
            new_status: TaskStatus,
            changed_by_id: int
    ) -> TaskShortRead:
        """Update the task's status and create a history record of the change."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.status = new_status

        history = TaskStatusHistory(
            task_id=task.id,
            changed_by_id=changed_by_id,
            new_status=new_status,
        )
        db.add(history)

        await db.commit()
        await db.refresh(task)

        return TaskShortRead.model_validate(task)

    async def get_user_related_tasks(
            self,
            db: AsyncSession,
            user_id: int,
            statuses: Optional[List[TaskStatus]] = None,
            priorities: Optional[List[TaskPriority]] = None
    ) -> List[TaskShortRead]:
        """Retrieves the tasks that the user is associated with, using the filters"""
        stmt = (
            select(Task)
            .options(selectinload(Task.assignees))
            .distinct()
            .where(
                or_(
                    Task.creator_id == user_id,
                    Task.assignees.any(User.id == user_id)
                )
            )
        )

        if statuses:
            stmt = stmt.where(Task.status.in_(statuses))
        else:
            stmt = stmt.where(Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS]))

        if priorities:
            stmt = stmt.where(Task.priority.in_(priorities))

        result = await db.execute(stmt)
        tasks = result.scalars().all()
        return [TaskShortRead.model_validate(task) for task in tasks]


tasks_crud = TaskCRUD()

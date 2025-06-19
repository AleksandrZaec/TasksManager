from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from backend.src.models import Task, TaskStatus, TaskPriority, User, TaskAssigneeAssociation, TeamUserAssociation
from backend.src.models.task_status_history import TaskStatusHistory
from backend.src.schemas import AssigneeInfo, TaskRead, TaskShortRead, TaskCreate, TaskUpdate
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy.orm import selectinload



class TaskCRUD(BaseCRUD):
    """CRUD for Task"""
    def __init__(self):
        super().__init__(model=Task, read_schema=TaskRead)

    async def create_task(self, db: AsyncSession, task_in: TaskCreate, creator_id: int, team_id: int) -> TaskShortRead:
        data = task_in.model_dump(exclude={"assignees"})
        data["creator_id"] = creator_id
        data["team_id"] = team_id

        task = Task(**data)
        db.add(task)

        try:
            await db.flush()
            await db.refresh(task)

            if task_in.assignees:
                unique_assignees = {(a.user_id, a.role or "EXECUTOR"): a for a in task_in.assignees}.values()
                user_ids = {a.user_id for a in unique_assignees}

                result = await db.execute(
                    select(User.id)
                    .join(TeamUserAssociation, TeamUserAssociation.user_id == User.id)
                    .where(
                        User.id.in_(user_ids),
                        TeamUserAssociation.team_id == team_id))
                valid_user_ids = set(result.scalars().all())

                missing_user_ids = user_ids - valid_user_ids
                if missing_user_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Users not found or not in team: {missing_user_ids}")

                for assignee in unique_assignees:
                    association = TaskAssigneeAssociation(
                        task_id=task.id,
                        user_id=assignee.user_id,
                        role=assignee.role or "EXECUTOR")
                    db.add(association)

            await db.commit()
            await db.refresh(task)

            return TaskShortRead.model_validate(task)

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create task: {e}")

    async def update_task(self, db: AsyncSession, task_id: int, task_in: TaskUpdate, creator_id: int) -> TaskShortRead:
        """Update an existing task and update the creator_id from the token."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task_in.model_dump(exclude_unset=True)
        task_data["creator_id"] = creator_id

        for field, value in task_data.items():
            setattr(task, field, value)

        try:
            await db.commit()
            await db.refresh(task)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return TaskShortRead.model_validate(task)

    async def get_all_task(self, db: AsyncSession) -> List[TaskShortRead]:
        """Retrieve all tasks from the database."""
        result = await db.execute(select(Task))
        tasks = result.scalars().all()
        return [TaskShortRead.model_validate(task) for task in tasks]

    async def get_task_by_id(self, db: AsyncSession, task_id: int) -> TaskRead:
        """Retrieve a task by ID with full assignee info from the association table."""
        result = await db.execute(
            select(Task).options(
                selectinload(Task.creator), selectinload(Task.assignee_associations)
                .selectinload(TaskAssigneeAssociation.user))
            .where(Task.id == task_id))

        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        assignees: list[AssigneeInfo] = [
            AssigneeInfo.model_validate({
                "id": assoc.user.id,
                "email": assoc.user.email,
                "first_name": assoc.user.first_name,
                "last_name": assoc.user.last_name,
                "assigned_at": assoc.assigned_at,
                "role": assoc.role
            })
            for assoc in task.assignee_associations
        ]

        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "creator_email": task.creator.email,
            "team_id": task.team_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "assignees": assignees
        }

        return TaskRead.model_validate(task_data)

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

        try:
            await db.commit()
            await db.refresh(task)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return TaskShortRead.model_validate(task)

    async def get_user_related_tasks(
            self,
            db: AsyncSession,
            user_id: int,
            statuses: Optional[List[TaskStatus]] = None,
            priorities: Optional[List[TaskPriority]] = None,
            team_id: Optional[int] = None
    ) -> List[TaskShortRead]:
        """Retrieves the tasks that the user is associated with, using the filters"""
        stmt = (
            select(Task)
            .options(
                selectinload(Task.assignee_associations)
                .selectinload(TaskAssigneeAssociation.user) )
            .distinct()
            .where(
                or_(
                    Task.creator_id == user_id,
                    Task.assignee_associations.any(
                        TaskAssigneeAssociation.user_id == user_id))))

        if team_id is not None:
            stmt = stmt.where(Task.team_id == team_id)

        if statuses:
            stmt = stmt.where(Task.status.in_(statuses))
        else:
            stmt = stmt.where(Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS]))

        if priorities:
            stmt = stmt.where(Task.priority.in_(priorities))

        result = await db.execute(stmt)
        tasks = result.scalars().all()
        return [TaskShortRead.model_validate(task) for task in tasks]

    async def get_team_tasks(
            self,
            db: AsyncSession,
            team_id: int,
            statuses: Optional[List[TaskStatus]] = None,
            priorities: Optional[List[TaskPriority]] = None
    ) -> List[TaskShortRead]:
        """Retrieve all tasks for a given team with optional filters."""
        stmt = select(Task).where(Task.team_id == team_id)

        if statuses is not None:
            stmt = stmt.where(Task.status.in_(statuses))
        else:
            stmt = stmt.where(Task.status.in_([TaskStatus.OPEN, TaskStatus.IN_PROGRESS]))

        if priorities:
            stmt = stmt.where(Task.priority.in_(priorities))

        result = await db.execute(stmt)
        tasks = result.scalars().all()
        return [TaskShortRead.model_validate(task) for task in tasks]


tasks_crud = TaskCRUD()

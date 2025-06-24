from sqladmin import ModelView
from fastapi import Request, HTTPException

from backend.src.config.db import sessionmaker
from backend.src.models import User, Team, Task, TeamUserAssociation, TaskAssigneeAssociation, TaskStatusHistory
from backend.src.schemas import UserCreate, UserUpdate, TeamCreate, TeamUpdate, TaskCreate, TaskUpdate
from backend.src.services.task import tasks_crud
from backend.src.services.team import teams_crud
from backend.src.services.user import users_crud


class BaseAdmin(ModelView):
    """Base admin view with common settings and access restriction."""
    page_size = 50
    can_view_details = True
    can_export = False

    def is_accessible(self, request: Request) -> bool:
        """Allow access only for superusers."""
        return request.session.get("is_superuser", False)


class UserAdmin(BaseAdmin, model=User):
    """Admin panel for managing users."""
    column_list = ["id", "email", "first_name", "last_name", "is_superuser"]
    column_searchable_list = ["email", "first_name", "last_name"]
    form_excluded_columns = ["password"]
    column_details_exclude_list = ["password"]

    async def create_model(self, request: Request, data: dict) -> User:
        """Create user with password hashing and validation using users_crud."""
        async with sessionmaker() as db:
            schema = UserCreate(**data)
            user_read = await users_crud.create(db, schema)
            return await db.get(User, user_read.id)

    async def update_model(self, request: Request, pk: int, data: dict) -> User:
        """Update user using custom logic (with password hashing and validation)."""
        async with sessionmaker() as db:
            schema = UserUpdate(**data)
            result = await users_crud.update(db, pk, schema)
            return await db.get(User, result.id)


class TeamAdmin(BaseAdmin, model=Team):
    """Admin panel for managing teams."""
    column_list = ["id", "name", "description"]
    column_searchable_list = ["name"]

    async def create_model(self, request: Request, data: dict) -> Team:
        """Create a new team with users and invite code using teams_crud."""
        creator_id = request.session.get("user_id")
        if not creator_id:
            raise HTTPException(status_code=401, detail="Unauthorized: no user_id in session")

        async with sessionmaker() as db:
            team_in = TeamCreate(**data)
            team_read = await teams_crud.create_team(db, team_in, creator_id)
            team = await db.get(Team, team_read.id)
            return team

    async def update_model(self, request: Request, pk: int, data: dict) -> Team:
        """Update team by ID with validation and invite code regeneration if needed."""
        async with sessionmaker() as db:
            team_in = TeamUpdate(**data)
            team_read = await teams_crud.update_team(db, pk, team_in)
            team = await db.get(Team, team_read.id)
            return team


class TaskAdmin(BaseAdmin, model=Task):
    """Admin panel for managing tasks."""
    column_list = ["id", "title", "status", "priority", "creator.email", "team.name", "deadline"]
    column_filters = ["status", "priority"]
    column_sortable_list = ["deadline"]
    column_labels = {"creator.email": "Создатель", "team.name": "Команда"}

    async def create_model(self, request: Request, data: dict) -> Task:
        """Create a task using custom CRUD logic to handle assignees, validation, and creator assignment."""
        creator_id = request.session.get("user_id")
        team_id = data.get("team_id")
        if not creator_id or not team_id:
            raise ValueError("creator_id and team_id must be available")

        async with sessionmaker() as db:
            task_in = TaskCreate(**data)
            task_read = await tasks_crud.create_task(db, task_in, creator_id, team_id)
            task = await db.get(Task, task_read.id)
            return task

    async def update_model(self, request: Request, pk: int, data: dict) -> Task:
        """Update a task using custom CRUD logic with validation."""
        creator_id = request.session.get("user_id")
        if not creator_id:
            raise ValueError("creator_id must be available")

        async with sessionmaker() as db:
            task_in = TaskUpdate(**data)
            task_read = await tasks_crud.update_task(db, pk, task_in, creator_id)
            task = await db.get(Task, task_read.id)
            return task


class TaskStatusHistoryAdmin(BaseAdmin, model=TaskStatusHistory):
    """Admin view for tracking task status history."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ["task.title", "new_status", "changed_by.email", "changed_at"]
    column_formatters = {"changed_at": lambda m, a: m.changed_at.strftime("%Y-%m-%d %H:%M")}
    column_default_sort = [("changed_at", True)]
    column_searchable_list = ["task.title", "changed_by.email"]
    column_labels = {
        "task.title": "Задача",
        "changed_by.email": "Кто изменил",
        "new_status": "Новый статус",
        "changed_at": "Дата изменения"
    }


class AssociationAdmin(BaseAdmin):
    """Read-only view for associative tables."""
    can_create = False
    can_edit = False
    can_delete = False


class TeamUserAssociationAdmin(AssociationAdmin, model=TeamUserAssociation):
    """Admin view for team-user relationships."""
    column_list = ["team.name", "user.email", "role", "joined_at"]
    column_labels = {"team.name": "Команда", "user.email": "Пользователь", "joined_at": "Дата вступления"}


class TaskAssigneeAssociationAdmin(AssociationAdmin, model=TaskAssigneeAssociation):
    """Admin view for task-assignee relationships."""
    column_list = ["task.title", "user.email", "assigned_at"]
    column_labels = {"task.title": "Задача", "user.email": "Исполнитель", "assigned_at": "Дата назначения"}

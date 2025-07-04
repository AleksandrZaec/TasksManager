from fastapi import FastAPI
from sqladmin import Admin

from src.admin.auth import AdminAuth
from src.config.db import engine
from src.config.settings import settings
from src.admin.views import (
    UserAdmin, TeamAdmin, TaskAdmin,
    TeamUserAssociationAdmin, TaskAssigneeAssociationAdmin,
    TaskStatusHistoryAdmin

)


def setup_admin(app: FastAPI) -> Admin:
    """Initialize and configure the admin panel."""
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
        base_url="/admin"
    )

    register_admin_views(admin)
    return admin


def register_admin_views(admin: Admin) -> None:
    """Register all admin views."""
    views = [
        UserAdmin, TeamAdmin, TaskAdmin,
        TeamUserAssociationAdmin, TaskAssigneeAssociationAdmin,
        TaskStatusHistoryAdmin
    ]

    for view in views:
        admin.add_view(view)

from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from sqlalchemy import select
from backend.src.models import User
from backend.src.config.db import SessionLocal
from backend.src.utils.security import verify_password
from fastapi import HTTPException


class AdminAuth(AuthenticationBackend):
    """Custom SQLAdmin authentication backend using superuser session check."""

    async def login(self, request: Request) -> bool:
        """Authenticate user by checking email and password. Only superusers are allowed to log in."""
        form = await request.form()
        email, password = form.get("username"), form.get("password")

        if not email or not password:
            return False

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            if not user or not verify_password(password, user.password):
                return False

            if not user.is_superuser:
                return False

            request.session.update({
                "user_id": user.id,
                "is_superuser": True
            })
            return True

    async def logout(self, request: Request) -> bool:
        """Clear session on logout."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Authorize request based on is_superuser flag in session."""
        return request.session.get("is_superuser", False)

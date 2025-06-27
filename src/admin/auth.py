from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from sqlalchemy import select
from src.config.db import SessionLocal
from src.models import User
from src.utils.security import verify_password
import logging

USER_ID = "user_id"
IS_SUPERUSER = "is_superuser"

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    """Custom SQLAdmin authentication backend using superuser session check."""

    def __init__(self):
        super().__init__()

    async def login(self, request: Request) -> bool:
        """Authenticate user by checking email and password. Only superusers are allowed to log in."""
        try:
            form = await request.form()
        except Exception as e:
            logger.error(f"Error reading the form: {e}")
            return False

        email, password = form.get("username"), form.get("password")

        if not email or not password:
            logger.warning("Login attempt without email or password")
            return False

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            if not user:
                logger.info(f"User with email {email} not found")
                return False

            if not verify_password(password, user.password):
                logger.info(f"Invalid password for the user {email}")
                return False

            if not user.is_superuser:
                logger.info(f"User {email} is not a superuser")
                return False

            request.session.update({
                USER_ID: user.id,
                IS_SUPERUSER: True
            })
            logger.info(f"User {email} has been successfully authorized as a superuser")
            return True

    async def logout(self, request: Request) -> bool:
        """Clear session on logout."""
        request.session.clear()
        logger.info("The session is cleared after logging out of the admin panel")
        return True

    async def authenticate(self, request: Request) -> bool:
        """Authorize request based on is_superuser flag in session."""
        return request.session.get(IS_SUPERUSER, False)

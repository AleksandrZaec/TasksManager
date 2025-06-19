import asyncio
import re
from getpass import getpass
from passlib.context import CryptContext
from backend.src.config.db import SessionLocal
from backend.src.models import User, UserRole
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def validate_name(name: str) -> bool:
    return 0 < len(name) <= 20


async def csu():
    """
    Interactive script to create an initial superuser (admin).
    Prompts for email, name, and password, validates inputs,
    and stores the user in the database if valid. python -m backend.src.admin.csu
    """
    email = input("Email: ").strip()
    if not validate_email(email):
        print("Invalid email format.")
        return

    first_name = input("First name: ").strip()
    if not validate_name(first_name):
        print("First name must be 1-20 characters long.")
        return

    last_name = input("Last name: ").strip()
    if not validate_name(last_name):
        print("Last name must be 1-20 characters long.")
        return

    while True:
        password = getpass("Password: ")
        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            print("Passwords do not match, try again.")
        elif len(password) < 6:
            print("Password should be at least 6 characters.")
        else:
            break

    hashed_password = pwd_context.hash(password)

    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing:
            print("User with this email already exists.")
            return

        user = User(
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True
        )

        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            await session.rollback()
            print(f"Failed to create user: {e}")
            return

        print(f"Congratulations, {user.last_name} {user.first_name}! Your account has been created.")
        print(f"Your login: {user.email}")


if __name__ == "__main__":
    asyncio.run(csu())

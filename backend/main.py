from fastapi import FastAPI

from backend.api import users

app = FastAPI(title="Team Manager")

app.include_router(users.router, prefix="/users", tags=["Users"])

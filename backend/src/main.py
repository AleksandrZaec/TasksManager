from fastapi import FastAPI

from backend.src.routers import user, team, task, auth

app = FastAPI(title="Team Manager")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(team.router, prefix="/teams", tags=["Teams"])
app.include_router(task.router, prefix="/tasks", tags=["Tasks"])

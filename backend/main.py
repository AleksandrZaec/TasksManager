from fastapi import FastAPI

from backend.api import users_api, teams_api

app = FastAPI(title="Team Manager")

app.include_router(users_api.router, prefix="/users", tags=["Users"])
app.include_router(teams_api.router, prefix="/teams", tags=["Teams"])
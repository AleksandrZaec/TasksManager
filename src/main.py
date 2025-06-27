from fastapi import FastAPI
from src.routers import user, team, task, auth, comment, evaluation, team_user, task_user, calendar
from src.routers import meeting
from src.admin import setup_admin
import logging

app = FastAPI(title="Team Manager")

admin = setup_admin(app)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(team.router, prefix="/teams", tags=["Teams"])
app.include_router(task.router, prefix="/tasks", tags=["Tasks"])
app.include_router(comment.router, prefix="/comments", tags=["Comments"])
app.include_router(evaluation.router, prefix="/evaluations", tags=["Evaluations"])
app.include_router(team_user.router, prefix="/teams_users", tags=["Team management"])
app.include_router(task_user.router, prefix="/tasks_users", tags=["Assignment complete tasks"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meetings"])
app.include_router(calendar.router, prefix="/calendars", tags=["Calendar"])

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


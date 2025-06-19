from fastapi import FastAPI
from backend.src.routers import user, team, task, auth, comment, evaluation, team_user, task_user, meeting
from backend.src.admin import setup_admin

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

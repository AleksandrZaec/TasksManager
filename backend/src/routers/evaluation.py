from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.deps.permissions import creator_only
from backend.src.models import User, Task
from backend.src.services.auth import get_current_user
from backend.src.schemas import EvaluationRead, EvaluationCreate
from backend.src.services.evaluation import evaluation_crud
from datetime import date

router = APIRouter()


@router.post(
    "/tasks/{task_id}/evaluations",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new evaluation for a task",
    description="Create a new evaluation for a task. Only the creator of the task can evaluate."
)
async def create_evaluation(
        task_id: int = Path(..., description="ID of the task to evaluate"),
        eva_in: EvaluationCreate = ...,
        current_user: User = Depends(creator_only(Task, id_path_param="task_id")),
        db: AsyncSession = Depends(get_db)
) -> EvaluationRead:
    """Create a new evaluation for a task by the current user."""
    return await evaluation_crud.create_evaluation(db, eva_in, task_id, current_user.id)


@router.put(
    "/{task_id}",
    response_model=EvaluationRead,
    summary="Update evaluation for a task",
    description="Update an evaluation for a task. Only the evaluator (creator) can update their evaluation."
)
async def update_evaluation(
        task_id: int = Path(..., description="ID of the task for which evaluation will be updated"),
        eva_in: EvaluationCreate = ...,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(creator_only(Task, id_path_param="task_id"))
) -> EvaluationRead:
    """Update an evaluation for a task (only by evaluator)."""
    return await evaluation_crud.update_evaluation(db, eva_in, task_id, current_user.id)


@router.get(
    "/my_evaluations",
    response_model=list[EvaluationRead],
    status_code=status.HTTP_200_OK,
    summary="Get all evaluations for the current user",
    description="Retrieve all evaluations that have been given to the current user."
)
async def read_my_evaluations(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> list[EvaluationRead]:
    """Get all the ratings given to the user."""
    return await evaluation_crud.get_evaluations_for_user(db, current_user.id)


@router.get(
    "/my_average_score",
    status_code=status.HTTP_200_OK,
    summary="Get average evaluation score for current user",
    description="Calculate and return the average evaluation score for the current user within a date range."
)
async def read_my_average_score(
        start_date: date = Query(..., description="Start date for averaging evaluations"),
        end_date: date = Query(..., description="End date for averaging evaluations"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> dict:
    """Calculate and return the average evaluation score for the current user."""
    avg_score = await evaluation_crud.get_avg_score_user(db, current_user.id, start_date, end_date)
    return {"average_score": avg_score}


@router.get(
    "/task/{task_id}/evaluations",
    response_model=list[EvaluationRead],
    status_code=status.HTTP_200_OK,
    summary="Get all evaluations for a task",
    description="Get all evaluations associated with a specific task by its ID."
)
async def read_evaluations_for_task(
        task_id: int = Path(..., description="ID of the task to get evaluations for"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> list[EvaluationRead]:
    """Get all evaluations for a specific task by task ID."""
    return await evaluation_crud.get_evaluations_for_task(db, task_id)

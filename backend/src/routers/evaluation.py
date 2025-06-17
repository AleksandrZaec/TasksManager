from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.models import User
from backend.src.services.auth import get_current_user
from backend.src.schemas.evaluation import EvaluationRead, EvaluationCreate
from backend.src.services.evaluation import evaluation_crud
from datetime import date

router = APIRouter()


@router.post("/tasks/{task_id}/evaluations", response_model=EvaluationRead)
async def create_evaluation(
        task_id: int,
        eva_in: EvaluationCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> EvaluationRead:
    """Create a new evaluation for a task by the current user."""
    return await evaluation_crud.create_evaluation(db, eva_in, task_id, current_user.id)


@router.put("/{task_id}", response_model=EvaluationRead)
async def update_evaluation(
        task_id: int,
        eva_in: EvaluationCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> EvaluationRead:
    """Update an evaluation for a task (only by evaluator)."""
    return await evaluation_crud.update_evaluation(db, eva_in, task_id, current_user.id)


@router.get("/my_evaluations", response_model=list[EvaluationRead], status_code=status.HTTP_200_OK)
async def read_my_evaluations(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> list[EvaluationRead]:
    """Get all the ratings given to the user."""
    return await evaluation_crud.get_evaluations_for_user(db, current_user.id)


@router.get("/my_average_score", status_code=status.HTTP_200_OK)
async def read_my_average_score(
        start_date: date = Query(...),
        end_date: date = Query(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> dict:
    """Calculate and return the average evaluation score for the current user"""
    avg_score = await evaluation_crud.get_avg_score_user(db, current_user.id, start_date, end_date)
    return {"average_score": avg_score}


@router.get("/task/{task_id}/evaluations", response_model=list[EvaluationRead], status_code=status.HTTP_200_OK)
async def read_evaluations_for_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),

) -> list[EvaluationRead]:
    """Get all evaluations for a specific task by task ID."""
    return await evaluation_crud.get_evaluations_for_task(db, task_id)

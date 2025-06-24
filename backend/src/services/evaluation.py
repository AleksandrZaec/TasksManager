from datetime import datetime, date, timezone, time
from backend.src.models import TaskAssigneeAssociation, EvaluationAssociation, User
from backend.src.services.basecrud import BaseCRUD
from backend.src.models.evaluation import Evaluation
from backend.src.schemas import EvaluationCreate, EvaluationRead
from sqlalchemy import and_, select, func
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class EvaluationCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(Evaluation, EvaluationRead)

    async def create_evaluation(
            self,
            db: AsyncSession,
            eva_in: EvaluationCreate,
            task_id: int,
            evaluator_id: int,
    ) -> EvaluationRead:
        """Create evaluation and associate with all assignees of the task."""
        existing = await db.execute(
            select(Evaluation).where(
                and_(
                    Evaluation.task_id == task_id,
                    Evaluation.evaluator_id == evaluator_id)))

        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Evaluation already exists for this evaluator")

        data = eva_in.model_dump()
        data["task_id"] = task_id
        data["evaluator_id"] = evaluator_id
        evaluation = Evaluation(**data)
        db.add(evaluation)

        try:
            await db.flush()

            result = await db.scalars(
                select(TaskAssigneeAssociation.user_id).where(
                    TaskAssigneeAssociation.task_id == task_id))
            recipient_ids = result.all()

            recipients = [
                EvaluationAssociation(evaluation_id=evaluation.id, user_id=user_id)
                for user_id in recipient_ids
            ]
            db.add_all(recipients)

            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        await db.refresh(evaluation)
        return EvaluationRead.model_validate(evaluation)

    async def update_evaluation(
            self,
            db: AsyncSession,
            eva_in: EvaluationCreate,
            task_id: int,
            evaluator_id: int,
    ) -> EvaluationRead:
        """Update an existing evaluation for a given task and evaluator."""
        result = await db.execute(
            select(Evaluation).where(
                and_(
                    Evaluation.task_id == task_id,
                    Evaluation.evaluator_id == evaluator_id)))
        evaluation = result.scalar_one_or_none()

        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        evaluation.score = eva_in.score
        evaluation.feedback = eva_in.feedback
        evaluation.updated_at = datetime.now(timezone.utc)

        try:
            await db.commit()
            await db.refresh(evaluation)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

        return EvaluationRead.model_validate(evaluation)

    async def get_evaluations_for_user(self, db: AsyncSession, user_id: int) -> list[EvaluationRead]:
        """Get all the ratings given to the user."""
        result = await db.scalars(
            select(EvaluationAssociation.evaluation_id).where(
                EvaluationAssociation.user_id == user_id))

        evaluation_ids = result.all()

        if not evaluation_ids:
            return []

        result = await db.scalars(
            select(Evaluation).where(Evaluation.id.in_(evaluation_ids)))

        evaluations = result.all()
        return [EvaluationRead.model_validate(e) for e in evaluations]

    async def get_avg_score_user(
            self,
            db: AsyncSession,
            user_id: int,
            start_date: date,
            end_date: date
    ) -> float | None:
        """Calculate the average user score for the period."""
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)

        result = await db.scalars(
            select(EvaluationAssociation.evaluation_id).where(
                EvaluationAssociation.user_id == user_id))

        evaluation_ids = result.all()

        if not evaluation_ids:
            return None

        result = await db.execute(
            select(func.avg(Evaluation.score))
            .where(
                and_(
                    Evaluation.id.in_(evaluation_ids),
                    Evaluation.created_at >= start_date,
                    Evaluation.created_at <= end_date)))

        avg_score = result.scalar_one_or_none()
        return avg_score

    async def get_evaluations_for_task(self, db: AsyncSession, task_id: int) -> list[EvaluationRead]:
        """Get all evaluations for a specific task, including evaluator full name."""
        stmt = (
            select(Evaluation, User.first_name, User.last_name, )
            .join(User, User.id == Evaluation.evaluator_id)
            .where(Evaluation.task_id == task_id))

        result = await db.execute(stmt)
        rows = result.all()

        evaluations = [
            EvaluationRead.model_validate(evaluation).model_copy(
                update={"evaluator_full_name": f"{first_name} {last_name}".strip()}
            )
            for evaluation, first_name, last_name in rows
        ]
        return evaluations


evaluation_crud = EvaluationCRUD()

import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from src.models import EvaluationAssociation
from src.schemas import EvaluationCreate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestEvaluationCRUDCreate:
    async def test_create_evaluation_success(
        self, test_session: AsyncSession, create_user, create_task, evaluation_crud
    ):
        """Create evaluation successfully."""
        user = await create_user(email="evaluator@example.com")
        task = await create_task(creator_id=user.id)

        eva_in = EvaluationCreate(score=5, feedback="Great")
        evaluation = await evaluation_crud.create_evaluation(test_session, eva_in, task.id, user.id)

        assert evaluation.score == 5
        assert evaluation.feedback == "Great"
        assert evaluation.task_id == task.id
        assert evaluation.evaluator_id == user.id

    async def test_create_evaluation_duplicate_raises(
        self, test_session: AsyncSession, create_user, create_task, evaluation_crud
    ):
        """Creating duplicate evaluation raises HTTP 400."""
        evaluator = await create_user(email="evaluator2@example.com")
        task = await create_task()

        eva_in = EvaluationCreate(score=5, feedback="Excellent")

        await evaluation_crud.create_evaluation(test_session, eva_in, task.id, evaluator.id)

        with pytest.raises(HTTPException) as exc_info:
            await evaluation_crud.create_evaluation(test_session, eva_in, task.id, evaluator.id)
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
class TestEvaluationCRUDUpdate:
    async def test_update_evaluation_success(
        self,
        test_session: AsyncSession,
        create_user,
        create_task,
        create_evaluation,
        evaluation_crud,
    ):
        """Update evaluation successfully."""
        evaluator = await create_user(email="evaluator3@example.com")
        task = await create_task()
        _ = await create_evaluation(task.id, evaluator.id, score=3, feedback="Okay")

        eva_in = EvaluationCreate(score=5, feedback="Updated feedback")

        updated = await evaluation_crud.update_evaluation(test_session, eva_in, task.id, evaluator.id)

        assert updated.score == 5
        assert updated.feedback == "Updated feedback"
        assert updated.updated_at is not None

    async def test_update_evaluation_not_found_raises(
        self, test_session: AsyncSession, create_user, create_task, evaluation_crud
    ):
        """Updating non-existent evaluation raises 404."""
        evaluator = await create_user(email="evaluator4@example.com")
        task = await create_task()

        eva_in = EvaluationCreate(score=4, feedback="Test")

        with pytest.raises(HTTPException) as exc_info:
            await evaluation_crud.update_evaluation(test_session, eva_in, task.id, evaluator.id)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail


@pytest.mark.asyncio
class TestEvaluationCRUDRead:
    async def test_get_evaluations_for_user(
        self,
        test_session: AsyncSession,
        create_user,
        create_task,
        create_evaluation,
        evaluation_crud,
    ):
        """Retrieve all evaluations for a user."""
        evaluator = await create_user(email="evaluator5@example.com")
        assignee = await create_user(email="assignee@example.com")
        task = await create_task()

        evaluation = await create_evaluation(task.id, evaluator.id, score=4, feedback="Good")

        assoc = EvaluationAssociation(evaluation_id=evaluation.id, user_id=assignee.id)
        test_session.add(assoc)
        await test_session.commit()

        results = await evaluation_crud.get_evaluations_for_user(test_session, assignee.id)

        assert any(e.score == 4 for e in results)

    async def test_get_evaluations_for_user_no_evals(self, test_session: AsyncSession, create_user, evaluation_crud):
        """Returns empty list if no evaluations for user."""
        user = await create_user(email="user_no_evals@example.com")

        results = await evaluation_crud.get_evaluations_for_user(test_session, user.id)

        assert results == []

    # async def test_get_avg_score_user(
    #     self, test_session: AsyncSession, create_user, create_task, create_evaluation, evaluation_crud
    # ):
    #     """Calculate average score for user in date range."""
    #     evaluator = await create_user(email="eval6@example.com")
    #     assignee = await create_user(email="assignee6@example.com")
    #     task = await create_task()
    #
    #     evaluation1 = await create_evaluation(task.id, evaluator.id, score=3, feedback="So-so")
    #     evaluation2 = await create_evaluation(task.id, evaluator.id, score=5, feedback="Great")
    #
    #     test_session.add_all(
    #         [
    #             EvaluationAssociation(evaluation_id=evaluation1.id, user_id=assignee.id),
    #             EvaluationAssociation(evaluation_id=evaluation2.id, user_id=assignee.id),
    #         ]
    #     )
    #     await test_session.commit()
    #
    #     start_date = date.today() - timedelta(days=1)
    #     end_date = date.today() + timedelta(days=1)
    #
    #     avg_score = await evaluation_crud.get_avg_score_user(test_session, assignee.id, start_date, end_date)
    #
    #     assert pytest.approx(4.0) == avg_score

    async def test_get_avg_score_user_no_evals(self, test_session: AsyncSession, create_user, evaluation_crud):
        """Returns None if no evaluations for user."""
        user = await create_user(email="user_no_evals2@example.com")

        start_date = date.today() - timedelta(days=1)
        end_date = date.today() + timedelta(days=1)

        avg_score = await evaluation_crud.get_avg_score_user(test_session, user.id, start_date, end_date)

        assert avg_score is None

    async def test_get_evaluations_for_task(
        self, test_session: AsyncSession, create_user, create_task, create_evaluation, evaluation_crud
    ):
        """Get all evaluations for a task with evaluator full name."""
        evaluator = await create_user(email="eval7@example.com", first_name="John", last_name="Doe")
        task = await create_task()

        _ = await create_evaluation(task.id, evaluator.id, score=4, feedback="Nice")

        results = await evaluation_crud.get_evaluations_for_task(test_session, task.id)

        assert any("John Doe" == e.evaluator_full_name for e in results)
from sqlalchemy import ForeignKey, DateTime, Integer, Text, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from backend.config.db import Base


class Evaluation(Base):
    """Evaluation model representing a manager's score (1–5) for a completed task."""
    __tablename__ = "evaluations"
    __table_args__ = (
        UniqueConstraint("task_id", "evaluator_id", name="unique_task_evaluator"),
        CheckConstraint('score >= 1 AND score <= 5', name='check_score_range')
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="evaluations",
        cascade="save-update"
    )
    evaluator: Mapped["User"] = relationship(
        "User",
        back_populates="evaluations_given",
        cascade="save-update"
    )

    @classmethod
    def average_score(cls, session, task_id: int) -> float:
        return session.query(func.avg(cls.score)).filter_by(task_id=task_id).scalar()
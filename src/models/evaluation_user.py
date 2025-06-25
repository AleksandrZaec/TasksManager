from sqlalchemy import ForeignKey, UniqueConstraint
from src.config.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EvaluationAssociation(Base):
    """
    Association table for the many-to-many relationship between evaluations and recipients.
    Tracks which users received specific evaluations.
    """
    __tablename__ = "evaluation_recipients"
    __table_args__ = (
        UniqueConstraint("evaluation_id", "user_id", name="uix_eval_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    evaluation: Mapped["Evaluation"] = relationship(back_populates="recipients")
    user: Mapped["User"] = relationship(back_populates="received_evaluations")


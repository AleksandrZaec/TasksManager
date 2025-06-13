from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, Text
from datetime import datetime, timezone
from backend.config.db import Base


class Comment(Base):
    """Comment model representing user comments on tasks."""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")

from sqlalchemy import ForeignKey, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from backend.src.config.db import Base
from backend.src.models.enum import TaskStatus


class TaskStatusHistory(Base):
    """Represents a record of a task status change, """
    __tablename__ = "task_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    new_status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    task: Mapped["Task"] = relationship("Task", back_populates="status_history")
    changed_by: Mapped["User"] = relationship("User")


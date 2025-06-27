from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, DateTime
from src.config.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TaskAssigneeAssociation(Base):
    """
    Association table for the many-to-many relationship between tasks and assignees.
    Allows multiple users to be assigned to a single task.
    """
    __tablename__ = "task_assignee_association"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    role: Mapped[str] = mapped_column(String(20), nullable=True)

    task: Mapped["Task"] = relationship(back_populates="assignee_associations")
    user: Mapped["User"] = relationship(back_populates="task_associations")

    def __str__(self):
        return f"TaskAssignee: task_id={self.task_id}, user_id={self.user_id}, role={self.role}"

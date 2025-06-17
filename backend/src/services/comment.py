from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models import Comment
from backend.src.schemas.comment import CommentRead, CommentBase, CommentUpdate
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException


class CommentCRUD(BaseCRUD):
    """CRUD operations for Comment model."""

    def __init__(self):
        super().__init__(Comment, CommentRead)

    async def create_comment(self, db: AsyncSession, task_id: int, obj_in: CommentBase, author_id: int) -> CommentRead:
        data = obj_in.model_dump()
        data["author_id"] = author_id
        data["task_id"] = task_id

        comment = Comment(**data)
        db.add(comment)
        await db.commit()

        result = await db.execute(
            select(Comment)
            .where(Comment.id == comment.id)
            .options(selectinload(Comment.author))
        )
        comment_with_author = result.scalar_one()

        return CommentRead.model_validate(comment_with_author)

    async def update_comment(
            self,
            db: AsyncSession,
            comment_id: int,
            comment_in: CommentUpdate,
            user_id: int,
    ) -> CommentRead:
        """Update comment content. Only the author can update their comment."""
        result = await db.execute(
            select(Comment)
            .where(Comment.id == comment_id)
            .options(selectinload(Comment.author))
        )
        comment: Comment | None = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the author of this comment")

        comment.content = comment_in.content

        await db.commit()

        return CommentRead.model_validate(comment)

    async def get_comments_by_task(self, db: AsyncSession, task_id: int) -> List[CommentRead]:
        """Retrieve all comments for a specific task, ordered by creation date descending."""
        result = await db.execute(
            select(Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
            .options(selectinload(Comment.author))
        )
        comments = result.scalars().all()

        return [CommentRead.model_validate(c) for c in comments]


comment_crud = CommentCRUD()

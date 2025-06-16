from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models import Comment
from backend.src.schemas.comment import CommentRead, CommentBase
from backend.src.services.basecrud import BaseCRUD
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class CommentCRUD(BaseCRUD):
    """CRUD operations for Comment model."""

    def __init__(self):
        super().__init__(Comment, CommentRead)

    async def create_comment(self, db: AsyncSession, task_id: int, obj_in: CommentBase, author_id: int) -> CommentRead:
        """Create a new comment with the given author ID."""
        data = obj_in.model_dump()
        data["author_id"] = author_id
        data["task_id"] = task_id

        comment = Comment(**data)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)

        await db.refresh(comment, attribute_names=["author"])
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

        # return [
        #     CommentRead(
        #         id=c.id,
        #         content=c.content,
        #         created_at=c.created_at,
        #         author_full_name=f"{c.author.first_name} {c.author.last_name}"
        #     )
        #     for c in comments
        # ]

        return [CommentRead.model_validate(c) for c in comments]


comment_crud = CommentCRUD()

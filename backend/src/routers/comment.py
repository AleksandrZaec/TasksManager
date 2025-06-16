from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.schemas.comment import CommentRead, CommentCreate, CommentUpdate
from backend.src.schemas.user import UserPayload
from backend.src.services.auth import get_current_user
from backend.src.services.comment import comment_crud

router = APIRouter()


@router.post("/", response_model=CommentRead)
async def create_comment(
        comment_in: CommentCreate,
        db: AsyncSession = Depends(get_db),
        user: UserPayload = Depends(get_current_user),
) -> CommentRead:
    """Create a new comment with the authenticated user as author."""
    return await comment_crud.create_comment(db, comment_in, author_id=user.id)


@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(comment_id: int, comment_in: CommentUpdate, db: AsyncSession = Depends(get_db)) -> CommentRead:
    """Update an existing comment by its ID."""
    return await comment_crud.update(db, comment_id, comment_in)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a comment by its ID."""
    await comment_crud.delete(db, comment_id)
    return None


@router.get("/task/{task_id}", response_model=List[CommentRead])
async def get_comments_by_task(task_id: int, db: AsyncSession = Depends(get_db)) -> List[CommentRead]:
    """Get all comments for a given task by task ID."""
    return await comment_crud.get_comments_by_task(db, task_id)




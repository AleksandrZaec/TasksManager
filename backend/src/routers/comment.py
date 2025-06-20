from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.db import get_db
from backend.src.deps.permissions import creator_only
from backend.src.models import Comment
from backend.src.schemas import CommentRead, CommentBase, CommentUpdate, UserPayload
from backend.src.services.auth import get_current_user
from backend.src.services.comment import comment_crud

router = APIRouter()


@router.post(
    "/{task_id}",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new comment",
    description="Create a new comment for the specified task. The authenticated user becomes the author."
)
async def create_comment(
        task_id: int = Path(..., description="ID of the task to add a comment to"),
        comment_in: CommentBase = ...,
        db: AsyncSession = Depends(get_db),
        user: UserPayload = Depends(get_current_user),
) -> CommentRead:
    """Create a new comment with the authenticated user as author."""
    return await comment_crud.create_comment(db, task_id, comment_in, user.id)


@router.put(
    "/{comment_id}",
    response_model=CommentRead,
    summary="Update a comment",
    description="Update an existing comment by its ID. Only the comment creator can update."
)
async def update_comment(
        comment_id: int = Path(..., description="ID of the comment to update"),
        comment_in: CommentUpdate = ...,
        db: AsyncSession = Depends(get_db),
        user: UserPayload = Depends(creator_only(Comment, id_path_param="comment_id"))
) -> CommentRead:
    """Update an existing comment by its ID."""
    return await comment_crud.update_comment(db, comment_id, comment_in, user.id)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
    description="Delete a comment by its ID. Only the comment creator can delete."
)
async def delete_comment(
        comment_id: int = Path(..., description="ID of the comment to delete"),
        db: AsyncSession = Depends(get_db),
        user: UserPayload = Depends(creator_only(Comment, id_path_param="comment_id"))
) -> None:
    """Delete a comment by its ID."""
    await comment_crud.delete(db, comment_id)
    return None


@router.get(
    "/task/{task_id}",
    response_model=List[CommentRead],
    summary="Get comments by task",
    description="Retrieve all comments for the specified task."
)
async def get_comments_by_task(
        task_id: int = Path(..., description="ID of the task to fetch comments for"),
        db: AsyncSession = Depends(get_db),
        user: UserPayload = Depends(get_current_user)
) -> List[CommentRead]:
    """Get all comments for a given task by task ID."""
    return await comment_crud.get_comments_by_task(db, task_id)
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from backend.src.schemas import CommentBase, CommentUpdate
from backend.src.services.comment import comment_crud


@pytest.mark.asyncio
class TestCommentCRUD:
    async def test_create_comment_success(self, test_session: AsyncSession, create_user, create_task):
        """Successfully create a comment for a task."""
        author = await create_user(email="commenter@example.com")
        task = await create_task(creator_id=author.id)

        comment_in = CommentBase(content="This is a comment")
        comment = await comment_crud.create_comment(test_session, task.id, comment_in, author.id)

        assert comment.content == "This is a comment"
        assert comment.author_id == author.id
        assert comment.author_full_name == f"{author.first_name} {author.last_name}"

    async def test_update_comment_success(self, test_session: AsyncSession, create_user, create_task):
        """Successfully update own comment."""
        author = await create_user(email="update_author@example.com")
        task = await create_task(creator_id=author.id)

        comment_in = CommentBase(content="Initial comment")
        created = await comment_crud.create_comment(test_session, task.id, comment_in, author.id)

        update_in = CommentUpdate(content="Updated content")
        updated = await comment_crud.update_comment(test_session, created.id, update_in, author.id)

        assert updated.content == "Updated content"
        assert updated.id == created.id

    async def test_update_comment_not_found(self, test_session: AsyncSession, create_user):
        """Raise 404 when updating a non-existent comment."""
        user = await create_user(email="notfound@example.com")
        update_in = CommentUpdate(content="Doesn't matter")

        with pytest.raises(HTTPException) as exc_info:
            await comment_crud.update_comment(test_session, 999999, update_in, user.id)

        assert exc_info.value.status_code == 404

    async def test_update_comment_wrong_author(self, test_session: AsyncSession, create_user, create_task):
        """Raise 403 when non-author tries to update a comment."""
        author = await create_user(email="author@example.com")
        other = await create_user(email="other@example.com")
        task = await create_task(creator_id=author.id)

        comment_in = CommentBase(content="Author's comment")
        comment = await comment_crud.create_comment(test_session, task.id, comment_in, author.id)

        update_in = CommentUpdate(content="Malicious update")
        with pytest.raises(HTTPException) as exc_info:
            await comment_crud.update_comment(test_session, comment.id, update_in, other.id)

        assert exc_info.value.status_code == 403

    async def test_get_comments_by_task(self, test_session: AsyncSession, create_user, create_task):
        """Retrieve all comments for a given task."""
        user = await create_user(email="commenter2@example.com")
        task = await create_task(creator_id=user.id)

        await comment_crud.create_comment(
            test_session, task.id, CommentBase(content="First"), user.id
        )
        await comment_crud.create_comment(
            test_session, task.id, CommentBase(content="Second"), user.id
        )

        comments = await comment_crud.get_comments_by_task(test_session, task.id)

        assert len(comments) == 2
        assert comments[0].content == "Second"
        assert comments[1].content == "First"

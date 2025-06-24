import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from backend.tests.integration.factories import TCreateSchema


@pytest.mark.asyncio
class TestBaseCRUDOperations:

    async def test_create_success(self, test_session: AsyncSession, crud):
        """Test successful creation of an object."""
        create_obj = TCreateSchema(name="test object")
        created = await crud.create(test_session, create_obj)
        assert created.id is not None
        assert created.name == "test object"

    async def test_get_by_id_success(self, test_session: AsyncSession, crud):
        """Test getting an object by id returns correct data."""
        create_obj = TCreateSchema(name="fetch test")
        created = await crud.create(test_session, create_obj)

        fetched = await crud.get_by_id(test_session, created.id)
        assert fetched.id == created.id
        assert fetched.name == "fetch test"

    async def test_get_all_returns_objects(self, test_session: AsyncSession, crud):
        """Test get_all returns a list including created objects."""
        create_obj = TCreateSchema(name="list test")
        created = await crud.create(test_session, create_obj)

        all_objs = await crud.get_all(test_session)
        assert any(o.id == created.id for o in all_objs)

    async def test_update_success(self, test_session: AsyncSession, crud):
        """Test updating an existing object updates fields correctly."""
        create_obj = TCreateSchema(name="to update")
        created = await crud.create(test_session, create_obj)

        update_obj = TCreateSchema(name="updated name")
        updated = await crud.update(test_session, created.id, update_obj)
        assert updated.name == "updated name"

    async def test_delete_success(self, test_session: AsyncSession, crud):
        """Test deleting an existing object removes it from the database."""
        create_obj = TCreateSchema(name="to delete")
        created = await crud.create(test_session, create_obj)

        await crud.delete(test_session, created.id)

        with pytest.raises(HTTPException) as exc_info:
            await crud.get_by_id(test_session, created.id)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
class TestBaseCRUDErrors:

    async def test_get_by_id_not_found_raises_404(self, test_session: AsyncSession, crud):
        """Test get_by_id raises HTTP 404 when object not found."""
        with pytest.raises(HTTPException) as exc_info:
            await crud.get_by_id(test_session, 999999)
        assert exc_info.value.status_code == 404

    async def test_update_not_found_raises_404(self, test_session: AsyncSession, crud):
        """Test update raises HTTP 404 when object not found."""
        update_obj = TCreateSchema(name="nonexistent update")
        with pytest.raises(HTTPException) as exc_info:
            await crud.update(test_session, 999999, update_obj)
        assert exc_info.value.status_code == 404

    async def test_delete_not_found_raises_404(self, test_session: AsyncSession, crud):
        """Test delete raises HTTP 404 when object not found."""
        with pytest.raises(HTTPException) as exc_info:
            await crud.delete(test_session, 999999)
        assert exc_info.value.status_code == 404

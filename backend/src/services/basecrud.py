from typing import Any, List, Type
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel


class BaseCRUD:
    def __init__(self, model: Type[Any], read_schema: Type[BaseModel]) -> None:
        """Initialize CRUD with model and Pydantic read schema."""
        self.model = model
        self.read_schema = read_schema

    async def get_by_id(self, db: AsyncSession, obj_id: int) -> BaseModel:
        """Get single object by its ID."""
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        res = self.read_schema.model_validate(obj)
        return res

    async def get_all(self, db: AsyncSession) -> List[BaseModel]:
        """Get all objects."""
        result = await db.execute(select(self.model))
        objs = result.scalars().all()
        res = [self.read_schema.model_validate(obj) for obj in objs]
        return res

    async def create(self, db: AsyncSession, obj_in: BaseModel) -> BaseModel:
        """Create a new object."""
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        res = self.read_schema.model_validate(obj)
        return res

    async def update(self, db: AsyncSession, obj_id: int, obj_in: BaseModel) -> BaseModel:
        """Update existing object by its ID."""
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")

        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(obj, field, value)

        await db.commit()
        await db.refresh(obj)
        res = self.read_schema.model_validate(obj)
        return res

    async def delete(self, db: AsyncSession, obj_id: int) -> dict:
        """Delete object by its ID."""
        result = await db.execute(select(self.model).where(self.model.id == obj_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")

        await db.delete(obj)
        await db.commit()
        return {"message": f"{self.model.__name__} deleted successfully", "id": obj_id}


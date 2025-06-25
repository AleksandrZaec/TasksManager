from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
from src.config.db import Base


class TModel(Base):
    """SQLAlchemy test model for CRUD operations."""
    __tablename__ = 'test_model'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class TReadSchema(BaseModel):
    """Pydantic schema for reading TestModel instances."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TCreateSchema(BaseModel):
    """Pydantic schema for creating/updating TestModel instances."""
    name: str

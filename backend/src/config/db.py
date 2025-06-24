from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.src.config.settings import settings

Base = declarative_base()


def get_async_engine():
    return create_async_engine(settings.DB_URL, echo=True)


def get_async_sessionmaker():
    return async_sessionmaker(bind=get_async_engine(), expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with get_async_sessionmaker()() as session:
        yield session


sessionmaker = get_async_sessionmaker()
engine = get_async_engine()

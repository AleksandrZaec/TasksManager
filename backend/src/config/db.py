from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.src.config.settings import settings

Base = declarative_base()

engine = create_async_engine(settings.DB_URL, echo=True)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

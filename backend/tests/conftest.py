import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.src.config.db import Base
from backend.src.config.settings import settings
from sqlalchemy import text


@pytest.fixture(scope="session", autouse=True)
def ensure_test_env():
    assert settings.MODE == "TEST", f"Expected MODE=TEST, got {settings.MODE}"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(settings.DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    sessionmaker_ = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with sessionmaker_() as session:
        yield session



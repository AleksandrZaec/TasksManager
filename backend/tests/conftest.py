import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.src.config.db import Base, get_db
from backend.src.config.settings import settings
from httpx import AsyncClient, ASGITransport
from backend.src.main import app


@pytest.fixture(scope="session", autouse=True)
def ensure_test_env():
    """Ensure tests run only in the TEST environment."""
    assert settings.MODE == "TEST", f"Expected MODE=TEST, got {settings.MODE}"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a fresh test database engine and recreate schema per test."""
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
    """Provide a new async DB session for each test."""
    sessionmaker_ = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with sessionmaker_() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_client(test_session):
    """Override get_db dependency and provide an async test client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
            transport=transport,
            base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.database import Base, get_database

# Use async PostgreSQL for testing
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskdb_test"

# Create async test engine
test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_database] = override_get_db


@pytest_asyncio.fixture
async def async_client():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    with TestClient(app) as c:
        yield c
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    # For sync test client compatibility
    with TestClient(app) as c:
        yield c
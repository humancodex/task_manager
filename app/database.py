from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Create async engine with proper connection pooling
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Use DeclarativeBase instead of declarative_base
class Base(DeclarativeBase):
    pass


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency"""
    async with AsyncSessionLocal() as session:
        yield session


async def check_database_health() -> bool:
    """Check database connectivity with detailed error logging"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
            logger.debug("Database health check passed")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        
        # Provide specific error context
        if "Connection refused" in str(e):
            logger.error("Database connection refused - PostgreSQL may not be running")
        elif "does not exist" in str(e):
            logger.error("Database does not exist - check database configuration")
        elif "authentication failed" in str(e):
            logger.error("Database authentication failed - check credentials")
        
        return False
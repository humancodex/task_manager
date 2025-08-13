from app.database import get_database
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency"""
    async for session in get_database():
        yield session
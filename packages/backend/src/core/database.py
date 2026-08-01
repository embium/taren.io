"""Database connection and session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from core.config import settings

# Create SQLAlchemy base
Base = declarative_base()

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# For async operations, use asyncpg driver
async_database_url = database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Create async engine
async_engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            # Catch BaseException to include asyncio.CancelledError
            import asyncio
            # Shield the rollback so it completes even if the task is cancelled
            await asyncio.shield(session.rollback())
            raise

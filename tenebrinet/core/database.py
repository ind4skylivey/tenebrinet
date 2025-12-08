# tenebrinet/core/database.py
"""
Database management for TenebriNET.

Provides async database connection management using SQLAlchemy with PostgreSQL.
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base


# Base class for SQLAlchemy models
Base = declarative_base()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost/tenebrinet_db",
)

# Create the async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,              # Maximum number of connections to keep in the pool
    max_overflow=10,           # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,           # Seconds to wait before giving up on getting a connection
    pool_recycle=3600,         # Recycle connections after 1 hour to prevent stale connections
    pool_pre_ping=True,        # Verify connections before using them
)

# Create a sessionmaker for async sessions
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called during application startup to ensure
    all model tables exist in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session.

    This is typically used as a FastAPI dependency to inject
    database sessions into route handlers.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

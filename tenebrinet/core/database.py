# tenebrinet/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

# Base class for our models
Base = declarative_base()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/tenebrinet_db")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=False) # echo=True for debugging SQL queries

# Create a sessionmaker for async sessions
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Important for keeping objects accessible after commit
)

async def init_db():
    """Initializes the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

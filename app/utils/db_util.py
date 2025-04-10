from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.app_config import settings

# Create async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    print("Connected DB URI:", settings.SQLALCHEMY_DATABASE_URI)
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Transaction context manager.
    
    Usage:
        async with transaction(session) as tx_session:
            # do something with tx_session
            # if no exception is raised, transaction is committed
            # if exception is raised, transaction is rolled back
    """
    if session.in_transaction():
        yield session
    else:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

@asynccontextmanager
async def nested_transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Nested transaction context manager.
    
    Usage:
        async with nested_transaction(session) as nested_session:
            # do something with nested_session
            # if no exception is raised, nested transaction is committed
            # if exception is raised, nested transaction is rolled back
    """
    async with session.begin_nested() as nested:
        try:
            yield session
            await nested.commit()
        except Exception:
            await nested.rollback()
            raise

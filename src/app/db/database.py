"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# Create async engine (lazy initialization)
_engine = None
_async_session_factory = None


def _get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        if settings.database_url:
            _engine = create_async_engine(
                settings.async_database_url,
                echo=settings.environment == "development",
                pool_pre_ping=True,
            )
    return _engine


def _get_session_factory():
    """Get or create the session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = _get_engine()
        if engine:
            _async_session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    session_factory = _get_session_factory()
    if session_factory is None:
        raise RuntimeError(
            "Database not configured. Set DATABASE_URL environment variable."
        )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables."""
    engine = _get_engine()
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

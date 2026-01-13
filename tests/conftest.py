"""Pytest configuration and shared fixtures."""

import os
import tempfile
import pytest
from collections.abc import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.database import Base, get_db
from app.main import app


# Create a temporary file for SQLite database
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")

# Async engine for the actual database operations
ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{_db_path}"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for table creation (TestClient runs in sync context)
SYNC_DATABASE_URL = f"sqlite:///{_db_path}"

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test and drop after."""
    # Import models to ensure they're registered with Base
    from app.db import models  # noqa: F401

    # Create tables using sync engine
    Base.metadata.create_all(bind=sync_engine)

    yield

    # Drop tables after test
    Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def pytest_sessionfinish(session, exitstatus):
    """Clean up temporary database file after all tests."""
    try:
        os.close(_db_fd)
        os.unlink(_db_path)
    except OSError:
        pass

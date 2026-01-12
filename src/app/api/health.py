"""Health check endpoint."""

import os
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    timestamp: str
    environment: str


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return the health status of the application.

    Returns:
        HealthResponse with current status, version, timestamp, and environment.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(UTC).isoformat(),
        environment=os.getenv("ENVIRONMENT", "development"),
    )

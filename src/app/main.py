"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.health import router as health_router
from app.api.routes import router as api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup: Initialize database if configured
    settings = get_settings()
    if settings.database_url:
        from app.db.database import init_db

        await init_db()

    yield

    # Shutdown: Cleanup if needed
    pass


app = FastAPI(
    title="CI/CD Pipeline Demo",
    description="A production-ready CI/CD pipeline demonstration",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(api_router)

# Prometheus metrics instrumentation
# This adds automatic metrics for all requests:
# - http_requests_total (counter)
# - http_request_duration_seconds (histogram)
# - http_request_size_bytes (summary)
# - http_response_size_bytes (summary)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

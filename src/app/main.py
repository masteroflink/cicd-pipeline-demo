"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.routes import router as api_router

app = FastAPI(
    title="CI/CD Pipeline Demo",
    description="A production-ready CI/CD pipeline demonstration",
    version="1.0.0",
)

# Include routers
app.include_router(health_router)
app.include_router(api_router)

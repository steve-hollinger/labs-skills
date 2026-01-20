"""Development environment example - FastAPI application."""

import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    environment: str
    debug: bool
    timestamp: str


class InfoResponse(BaseModel):
    """Application info response."""

    name: str
    version: str
    environment: str
    features: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting application...")
    if os.getenv("DEBUGPY_ENABLE") == "true":
        try:
            import debugpy

            debugpy.listen(("0.0.0.0", 5678))
            print("Debugpy listening on port 5678")
        except Exception as e:
            print(f"Could not start debugpy: {e}")
    yield
    # Shutdown
    print("Shutting down application...")


app = FastAPI(
    title="Dev Environment Example",
    description="Demonstrates Docker Compose development environment",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hello from Development Environment!",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        environment=os.getenv("ENVIRONMENT", "unknown"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/info", response_model=InfoResponse)
async def info():
    """Application info endpoint."""
    features = []
    if os.getenv("DEBUG") == "true":
        features.append("debug-mode")
    if os.getenv("DEBUGPY_ENABLE") == "true":
        features.append("remote-debugging")
    if os.getenv("DATABASE_URL"):
        features.append("database")
    if os.getenv("REDIS_URL"):
        features.append("cache")

    return InfoResponse(
        name="dev-environment-app",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "unknown"),
        features=features,
    )


@app.get("/config")
async def config():
    """Show current configuration (development only)."""
    if os.getenv("ENVIRONMENT") != "development":
        return {"error": "Only available in development"}

    return {
        "environment": os.getenv("ENVIRONMENT"),
        "debug": os.getenv("DEBUG"),
        "database_url": os.getenv("DATABASE_URL", "").replace(
            os.getenv("DATABASE_URL", "").split("@")[0].split("//")[1]
            if "@" in os.getenv("DATABASE_URL", "")
            else "",
            "***:***",
        )
        if os.getenv("DATABASE_URL")
        else None,
        "redis_url": os.getenv("REDIS_URL"),
    }

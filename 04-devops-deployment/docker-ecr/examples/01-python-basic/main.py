"""Basic Python FastAPI application for Docker example."""

from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Python Docker Example",
    description="Demonstrates Dockerfile best practices",
    version="1.0.0",
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str


class MessageResponse(BaseModel):
    """Message response model."""

    message: str
    container_id: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return health status of the application."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.get("/", response_model=MessageResponse)
def root() -> MessageResponse:
    """Return a welcome message."""
    import socket

    return MessageResponse(
        message="Hello from Docker!",
        container_id=socket.gethostname(),
    )


@app.get("/info")
def info() -> dict:
    """Return application and environment information."""
    import os
    import sys

    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "user": os.getenv("USER", "unknown"),
        "working_directory": os.getcwd(),
    }

"""Simple FastAPI application demonstrating Docker Compose web stack."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI
import asyncpg
import redis.asyncio as redis

app = FastAPI(title="Web Stack Example")

# Configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://localhost:5432/webapp")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


@app.get("/")
async def root():
    """Return welcome message."""
    return {"message": "Hello from Docker Compose Web Stack!"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/db-check")
async def db_check():
    """Check database connectivity."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        return {"status": "connected", "version": version}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/cache-check")
async def cache_check():
    """Check Redis connectivity."""
    try:
        r = redis.from_url(REDIS_URL)
        await r.ping()
        await r.set("test_key", "test_value")
        value = await r.get("test_key")
        await r.close()
        return {"status": "connected", "test_value": value.decode()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/status")
async def status():
    """Return full status of all services."""
    db_status = await db_check()
    cache_status = await cache_check()

    return {
        "api": "healthy",
        "database": db_status,
        "cache": cache_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

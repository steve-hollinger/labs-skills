"""API for three-tier application exercise."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI
import asyncpg

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://localhost:5432/app")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/db-status")
async def db_status():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        return {"status": "connected", "version": version[:50] + "..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

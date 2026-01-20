"""User microservice."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="User Service")

DATABASE_URL = os.getenv("DATABASE_URL")


@app.get("/")
async def root():
    return {"service": "user-service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "user-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/users")
async def list_users():
    """Return list of users (mock data)."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
        ]
    }


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Return single user."""
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

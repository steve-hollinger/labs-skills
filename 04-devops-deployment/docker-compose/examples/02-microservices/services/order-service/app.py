"""Order microservice."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Order Service")

DATABASE_URL = os.getenv("DATABASE_URL")


@app.get("/")
async def root():
    return {"service": "order-service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "order-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/orders")
async def list_orders():
    """Return list of orders (mock data)."""
    return {
        "orders": [
            {"id": 1, "user_id": 1, "total": 99.99, "status": "completed"},
            {"id": 2, "user_id": 2, "total": 149.99, "status": "pending"},
            {"id": 3, "user_id": 1, "total": 29.99, "status": "shipped"},
        ]
    }


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Return single order."""
    return {
        "id": order_id,
        "user_id": 1,
        "total": 99.99,
        "status": "completed",
        "items": [
            {"product": "Widget", "quantity": 2, "price": 49.99},
        ],
    }

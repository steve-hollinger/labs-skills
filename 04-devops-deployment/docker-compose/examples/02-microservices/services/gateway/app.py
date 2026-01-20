"""API Gateway for microservices example."""

import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="API Gateway")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")


@app.get("/")
async def root():
    return {"service": "gateway", "message": "Microservices API Gateway"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "gateway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status")
async def status():
    """Check status of all downstream services."""
    results = {"gateway": "healthy"}

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Check user service
        try:
            resp = await client.get(f"{USER_SERVICE_URL}/health")
            results["user-service"] = resp.json()
        except Exception as e:
            results["user-service"] = {"status": "error", "message": str(e)}

        # Check order service
        try:
            resp = await client.get(f"{ORDER_SERVICE_URL}/health")
            results["order-service"] = resp.json()
        except Exception as e:
            results["order-service"] = {"status": "error", "message": str(e)}

    return results


@app.get("/users")
async def get_users():
    """Proxy to user service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{USER_SERVICE_URL}/users")
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))


@app.get("/orders")
async def get_orders():
    """Proxy to order service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{ORDER_SERVICE_URL}/orders")
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))

"""Example 4: Async Endpoints and Middleware

This example demonstrates async/await usage and middleware
for cross-cutting concerns like logging, timing, and CORS.
"""

import asyncio
import time
from datetime import datetime
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel


# =============================================================================
# Models
# =============================================================================


class AsyncResult(BaseModel):
    """Result from async operation."""

    source: str
    data: dict
    duration_ms: float


class DashboardData(BaseModel):
    """Combined dashboard data."""

    users: dict
    orders: dict
    stats: dict
    total_duration_ms: float


# =============================================================================
# Simulated Async Services
# =============================================================================


async def fetch_users_async(delay: float = 0.1) -> dict:
    """Simulate async API call to user service."""
    await asyncio.sleep(delay)
    return {
        "count": 150,
        "active": 120,
        "new_today": 5,
    }


async def fetch_orders_async(delay: float = 0.1) -> dict:
    """Simulate async API call to order service."""
    await asyncio.sleep(delay)
    return {
        "pending": 25,
        "completed": 450,
        "revenue": 15420.50,
    }


async def fetch_stats_async(delay: float = 0.1) -> dict:
    """Simulate async API call to stats service."""
    await asyncio.sleep(delay)
    return {
        "page_views": 10500,
        "conversion_rate": 0.032,
        "avg_session": "4m 23s",
    }


def fetch_data_sync(source: str, delay: float = 0.1) -> dict:
    """Synchronous version for comparison."""
    time.sleep(delay)
    return {"source": source, "data": "sync data"}


# =============================================================================
# FastAPI Application with Middleware
# =============================================================================

app = FastAPI(
    title="Async and Middleware Example",
    description="Demonstrates async endpoints and middleware patterns",
    version="1.0.0",
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Middleware: Request Timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    """Add X-Process-Time header to all responses."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# Custom Middleware: Request Logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log all requests and responses."""
    start_time = datetime.now()
    print(f"[{start_time.isoformat()}] {request.method} {request.url.path}")

    response = await call_next(request)

    duration = (datetime.now() - start_time).total_seconds() * 1000
    print(f"[{datetime.now().isoformat()}] Response: {response.status_code} ({duration:.2f}ms)")

    return response


# Custom Middleware: Request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable) -> Response:
    """Add unique request ID to headers."""
    request_id = f"req-{int(time.time() * 1000)}"
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# =============================================================================
# Exception Handler
# =============================================================================


class AppException(Exception):
    """Custom application exception."""

    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


# =============================================================================
# Async Endpoints
# =============================================================================


@app.get("/async/users", response_model=AsyncResult)
async def get_users_async():
    """Async endpoint to fetch user data."""
    start = time.perf_counter()
    data = await fetch_users_async()
    duration = (time.perf_counter() - start) * 1000

    return AsyncResult(source="users", data=data, duration_ms=duration)


@app.get("/async/orders", response_model=AsyncResult)
async def get_orders_async():
    """Async endpoint to fetch order data."""
    start = time.perf_counter()
    data = await fetch_orders_async()
    duration = (time.perf_counter() - start) * 1000

    return AsyncResult(source="orders", data=data, duration_ms=duration)


@app.get("/async/dashboard", response_model=DashboardData)
async def get_dashboard_parallel():
    """Fetch all dashboard data in parallel.

    This demonstrates the power of async - all three API calls
    run concurrently, reducing total time.
    """
    start = time.perf_counter()

    # Run all fetches in parallel
    users, orders, stats = await asyncio.gather(
        fetch_users_async(),
        fetch_orders_async(),
        fetch_stats_async(),
    )

    duration = (time.perf_counter() - start) * 1000

    return DashboardData(
        users=users,
        orders=orders,
        stats=stats,
        total_duration_ms=duration,
    )


@app.get("/async/dashboard-sequential")
async def get_dashboard_sequential():
    """Fetch dashboard data sequentially for comparison.

    This shows why parallel execution is important -
    sequential takes 3x longer.
    """
    start = time.perf_counter()

    # Sequential calls (slower)
    users = await fetch_users_async()
    orders = await fetch_orders_async()
    stats = await fetch_stats_async()

    duration = (time.perf_counter() - start) * 1000

    return {
        "users": users,
        "orders": orders,
        "stats": stats,
        "total_duration_ms": duration,
        "note": "Sequential execution - compare to /async/dashboard",
    }


@app.get("/sync/data")
def get_sync_data():
    """Synchronous endpoint for comparison.

    Note: This uses 'def' not 'async def'.
    FastAPI runs it in a thread pool.
    """
    start = time.perf_counter()
    data = fetch_data_sync("sync-endpoint")
    duration = (time.perf_counter() - start) * 1000

    return {
        "data": data,
        "duration_ms": duration,
        "note": "Synchronous endpoint - runs in thread pool",
    }


@app.get("/error/custom")
async def trigger_custom_error():
    """Trigger a custom application error."""
    raise AppException(detail="This is a custom error", status_code=400)


@app.get("/error/unhandled")
async def trigger_unhandled_error():
    """Trigger an unhandled error."""
    raise ValueError("This is an unhandled error")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


def demonstrate_async_middleware():
    """Demonstrate async and middleware features."""
    print("Example 4: Async Endpoints and Middleware")
    print("=" * 50)

    client = TestClient(app)

    # 1. Check middleware headers
    print("\n1. Middleware Headers:")
    response = client.get("/health")
    print(f"   X-Process-Time: {response.headers.get('X-Process-Time')}")
    print(f"   X-Request-ID: {response.headers.get('X-Request-ID')}")

    # 2. Single async endpoint
    print("\n2. Single async endpoint (/async/users):")
    response = client.get("/async/users")
    data = response.json()
    print(f"   Duration: {data['duration_ms']:.2f}ms")
    print(f"   Data: {data['data']}")

    # 3. Parallel async calls
    print("\n3. Parallel async dashboard (/async/dashboard):")
    response = client.get("/async/dashboard")
    data = response.json()
    print(f"   Total duration: {data['total_duration_ms']:.2f}ms")
    print(f"   (3 calls with 100ms each, run in parallel)")

    # 4. Sequential async calls for comparison
    print("\n4. Sequential async dashboard (/async/dashboard-sequential):")
    response = client.get("/async/dashboard-sequential")
    data = response.json()
    print(f"   Total duration: {data['total_duration_ms']:.2f}ms")
    print(f"   (3 calls with 100ms each, run sequentially)")

    # 5. Compare parallel vs sequential
    print("\n5. Performance Comparison:")
    # Run parallel
    start = time.perf_counter()
    parallel = client.get("/async/dashboard")
    parallel_time = (time.perf_counter() - start) * 1000

    # Run sequential
    start = time.perf_counter()
    sequential = client.get("/async/dashboard-sequential")
    sequential_time = (time.perf_counter() - start) * 1000

    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"   Parallel: {parallel_time:.2f}ms")
    print(f"   Sequential: {sequential_time:.2f}ms")
    print(f"   Speedup: {speedup:.2f}x")

    # 6. Sync endpoint (runs in thread pool)
    print("\n6. Sync endpoint (/sync/data):")
    response = client.get("/sync/data")
    data = response.json()
    print(f"   Duration: {data['duration_ms']:.2f}ms")
    print(f"   Note: {data['note']}")

    # 7. Custom error handling
    print("\n7. Custom error handler:")
    response = client.get("/error/custom")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 8. General error handler
    print("\n8. General error handler:")
    response = client.get("/error/unhandled")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # 9. CORS headers (simulated preflight)
    print("\n9. CORS Headers (OPTIONS request):")
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    print(f"   Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    print(f"   Allow-Methods: {response.headers.get('access-control-allow-methods')}")

    # 10. Summary
    print("\n10. Features Demonstrated:")
    print("    - Async endpoints with 'async def'")
    print("    - Parallel execution with asyncio.gather")
    print("    - Request timing middleware")
    print("    - Request ID middleware")
    print("    - Request logging middleware")
    print("    - CORS middleware")
    print("    - Custom exception handlers")
    print("    - Global exception handler")

    print("\nExample completed successfully!")


def main():
    """Run the example demonstration."""
    demonstrate_async_middleware()


if __name__ == "__main__":
    main()

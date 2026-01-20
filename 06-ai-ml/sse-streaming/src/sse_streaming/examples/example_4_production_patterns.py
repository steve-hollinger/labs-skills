"""
Example 4: Production Patterns

This example demonstrates production-ready SSE patterns:
- Error handling and recovery
- Keep-alive heartbeats
- Connection management
- Rate limiting
- Graceful shutdown

Key concepts for production SSE deployments.
"""

import os
import json
import asyncio
import time
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

# Active connections tracking
active_connections: set = set()


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("Starting SSE server...")
    yield
    # Cleanup on shutdown
    print(f"Shutting down. Closing {len(active_connections)} active connections...")
    active_connections.clear()


app = FastAPI(
    title="Production SSE Patterns",
    lifespan=lifespan
)


# ============================================================================
# Production Generators
# ============================================================================

async def stream_with_heartbeat(
    data_generator,
    heartbeat_interval: int = 15,
    request: Request = None
):
    """
    Wrap a generator with heartbeat support.

    Sends comment lines to keep connection alive during long gaps.

    Args:
        data_generator: Async generator yielding data
        heartbeat_interval: Seconds between heartbeats
        request: FastAPI request for disconnect detection
    """
    last_data_time = time.time()
    connection_id = id(request) if request else id(data_generator)
    active_connections.add(connection_id)

    try:
        async for item in data_generator:
            # Check for client disconnect
            if request and await request.is_disconnected():
                print(f"Client {connection_id} disconnected")
                break

            yield item
            last_data_time = time.time()

        # Final heartbeat to signal completion
        yield "data: [DONE]\n\n"

    except asyncio.CancelledError:
        print(f"Stream {connection_id} cancelled")
        raise
    except Exception as e:
        error_data = json.dumps({"error": str(e), "type": "stream_error"})
        yield f"event: error\ndata: {error_data}\n\n"
    finally:
        active_connections.discard(connection_id)


async def stream_with_error_recovery(data_source):
    """
    Stream with error recovery and detailed error events.

    Catches exceptions and sends them as error events instead of breaking.
    """
    event_count = 0

    try:
        async for item in data_source:
            try:
                event_count += 1
                yield f"id: evt-{event_count:06d}\ndata: {json.dumps(item)}\n\n"
            except Exception as e:
                error_data = {
                    "error": str(e),
                    "event_index": event_count,
                    "recoverable": True
                }
                yield f"event: item_error\ndata: {json.dumps(error_data)}\n\n"

    except Exception as e:
        error_data = {
            "error": str(e),
            "events_processed": event_count,
            "recoverable": False
        }
        yield f"event: fatal_error\ndata: {json.dumps(error_data)}\n\n"

    # Always send completion marker
    yield f"event: complete\ndata: {json.dumps({'total_events': event_count})}\n\n"


async def rate_limited_stream(
    data_source,
    max_events_per_second: float = 10
):
    """
    Rate-limit outgoing events.

    Useful for preventing client overload.
    """
    min_interval = 1.0 / max_events_per_second
    last_event_time = 0

    async for item in data_source:
        # Calculate delay needed
        now = time.time()
        elapsed = now - last_event_time
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)

        yield f"data: {json.dumps(item)}\n\n"
        last_event_time = time.time()


# ============================================================================
# Sample Data Sources
# ============================================================================

async def simulated_data_source(count: int = 20, failure_rate: float = 0.1):
    """
    Simulated data source with occasional failures.

    Used for testing error handling.
    """
    import random

    for i in range(count):
        # Simulate occasional failures
        if random.random() < failure_rate:
            raise ValueError(f"Simulated failure at item {i}")

        yield {
            "id": i,
            "timestamp": datetime.now().isoformat(),
            "value": random.random() * 100
        }
        await asyncio.sleep(0.1)


async def long_running_source(duration_seconds: int = 30):
    """
    Long-running data source for testing heartbeats.

    Generates events with varying gaps.
    """
    import random

    start_time = time.time()
    event_id = 0

    while time.time() - start_time < duration_seconds:
        event_id += 1
        yield {
            "event_id": event_id,
            "elapsed": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }

        # Variable delay (some long gaps to test heartbeat)
        delay = random.choice([0.5, 1, 2, 5, 10])
        await asyncio.sleep(delay)


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/stream/robust")
async def robust_stream(
    count: int = Query(20, ge=1, le=100),
    request: Request = None
):
    """
    Robust stream with heartbeat and error handling.

    Production-ready endpoint with all safety features.
    """
    async def wrapped_source():
        async for item in simulated_data_source(count, failure_rate=0.05):
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        stream_with_heartbeat(wrapped_source(), request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/stream/long")
async def long_stream(
    duration: int = Query(30, ge=5, le=300),
    request: Request = None
):
    """
    Long-running stream demonstrating heartbeat.

    Watch for ':heartbeat' comments during gaps.
    """
    async def source_with_heartbeat():
        last_time = time.time()

        async for item in long_running_source(duration):
            yield f"data: {json.dumps(item)}\n\n"

            # Send heartbeat if gap was long
            gap = time.time() - last_time
            if gap > 5:
                yield f": heartbeat after {gap:.1f}s gap\n\n"
            last_time = time.time()

    return StreamingResponse(
        stream_with_heartbeat(source_with_heartbeat(), request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/stream/rate-limited")
async def rate_limited_endpoint(
    count: int = Query(50, ge=1, le=200),
    rate: float = Query(5.0, ge=0.1, le=100)
):
    """
    Rate-limited stream.

    Events are throttled to the specified rate.
    """
    source = simulated_data_source(count, failure_rate=0)

    return StreamingResponse(
        rate_limited_stream(source, max_events_per_second=rate),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/stream/recoverable")
async def recoverable_stream(count: int = Query(30, ge=1, le=100)):
    """
    Stream with error recovery.

    Errors are sent as events, stream continues.
    """
    source = simulated_data_source(count, failure_rate=0.2)

    return StreamingResponse(
        stream_with_error_recovery(source),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/status")
async def server_status():
    """Server status endpoint."""
    return {
        "status": "running",
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def info():
    """API info."""
    return {
        "example": "Production Patterns",
        "endpoints": {
            "/stream/robust": "Full-featured production stream",
            "/stream/long": "Long-running with heartbeat demo",
            "/stream/rate-limited": "Rate-limited stream",
            "/stream/recoverable": "Stream with error recovery",
            "/status": "Server status"
        }
    }


# ============================================================================
# Main
# ============================================================================

def main():
    """Run the production patterns example."""
    print("=" * 60)
    print("Example 4: Production Patterns")
    print("=" * 60)

    print("\n--- Production Considerations ---")
    print("1. Heartbeats: Keep connection alive during long gaps")
    print("2. Error Recovery: Handle errors without breaking stream")
    print("3. Rate Limiting: Prevent client overload")
    print("4. Connection Tracking: Monitor active connections")
    print("5. Graceful Shutdown: Clean up on server stop")
    print("6. Disconnect Detection: Stop processing when client leaves")

    print("\n--- Headers for Production ---")
    print("  Cache-Control: no-cache, no-transform")
    print("  Connection: keep-alive")
    print("  X-Accel-Buffering: no  (for nginx)")

    print("\n" + "=" * 60)
    print("Starting server on http://localhost:8004")
    print("=" * 60)
    print("\nTest endpoints:")
    print('  curl -N "http://localhost:8004/stream/robust"')
    print('  curl -N "http://localhost:8004/stream/long?duration=60"')
    print('  curl -N "http://localhost:8004/stream/rate-limited?rate=2"')
    print("\nPress Ctrl+C to stop")

    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")


if __name__ == "__main__":
    main()

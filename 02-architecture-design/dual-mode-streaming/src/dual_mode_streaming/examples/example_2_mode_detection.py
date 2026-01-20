"""Example 2: Mode Detection and Switching.

This example demonstrates automatic mode switching between streaming and
batch responses based on HTTP headers and query parameters.

Run with: make example-2
Or: uv run python -m dual_mode_streaming.examples.example_2_mode_detection
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from dual_mode_streaming.modes import ResponseMode, detect_response_mode, negotiate_mode

app = FastAPI(title="Mode Detection Example")


# Sample data generator
async def generate_items() -> AsyncGenerator[dict, None]:
    """Generate sample items with simulated delay.

    Yields:
        Dictionary items with id and name.
    """
    for i in range(1, 6):
        await asyncio.sleep(0.2)
        yield {"id": i, "name": f"Item {i}", "value": i * 10}


# Pattern 1: Simple query parameter switch
@app.get("/items/simple")
async def get_items_simple(stream: bool = Query(default=False)):
    """Get items with explicit stream parameter.

    Args:
        stream: If True, stream response; otherwise return batch.

    Returns:
        StreamingResponse or JSONResponse based on stream parameter.
    """
    if stream:
        async def stream_items() -> AsyncGenerator[str, None]:
            async for item in generate_items():
                yield f"data: {json.dumps(item)}\n\n"

        return StreamingResponse(
            stream_items(),
            media_type="text/event-stream",
        )

    # Batch mode - collect all items
    items = [item async for item in generate_items()]
    return JSONResponse({"items": items, "count": len(items)})


# Pattern 2: Accept header detection
@app.get("/items/header")
async def get_items_header(request: Request):
    """Get items with mode detected from Accept header.

    Clients requesting 'text/event-stream' get streaming response.

    Args:
        request: The incoming request for header inspection.

    Returns:
        Response in detected mode.
    """
    mode = detect_response_mode(request)

    if mode == ResponseMode.STREAM:
        async def stream_items() -> AsyncGenerator[str, None]:
            async for item in generate_items():
                yield f"data: {json.dumps(item)}\n\n"

        return StreamingResponse(
            stream_items(),
            media_type="text/event-stream",
        )

    items = [item async for item in generate_items()]
    return JSONResponse({"items": items, "mode": "batch"})


# Pattern 3: Full negotiation with dependency
@app.get("/items/negotiate")
async def get_items_negotiate(mode: ResponseMode = Depends(negotiate_mode)):
    """Get items with full mode negotiation.

    Uses negotiate_mode dependency which checks:
    1. Explicit 'stream' query parameter
    2. Explicit 'format' query parameter
    3. Accept header

    Args:
        mode: Negotiated response mode from dependency.

    Returns:
        Response in negotiated mode.
    """
    if mode == ResponseMode.STREAM:
        async def stream_items() -> AsyncGenerator[str, None]:
            async for item in generate_items():
                yield f"data: {json.dumps(item)}\n\n"
            yield f"event: complete\ndata: {json.dumps({'status': 'done'})}\n\n"

        return StreamingResponse(
            stream_items(),
            media_type="text/event-stream",
        )

    items = [item async for item in generate_items()]
    return JSONResponse({
        "items": items,
        "count": len(items),
        "mode": mode.value,
    })


# Pattern 4: Unified handler pattern
class DataService:
    """Service that provides data in both modes."""

    async def get_batch(self) -> list[dict]:
        """Get all items as a batch.

        Returns:
            List of all items.
        """
        return [item async for item in self._generate()]

    async def get_stream(self) -> AsyncGenerator[dict, None]:
        """Stream items one at a time.

        Yields:
            Individual items.
        """
        async for item in self._generate():
            yield item

    async def _generate(self) -> AsyncGenerator[dict, None]:
        """Internal generator shared by both modes.

        Yields:
            Dictionary items.
        """
        for i in range(1, 6):
            await asyncio.sleep(0.2)
            yield {"id": i, "name": f"Product {i}", "price": i * 9.99}


def get_data_service() -> DataService:
    """Dependency injection for DataService."""
    return DataService()


@app.get("/products")
async def get_products(
    mode: ResponseMode = Depends(negotiate_mode),
    service: DataService = Depends(get_data_service),
):
    """Get products using the unified handler pattern.

    The DataService provides the same data through either batch or stream
    interface, keeping the business logic separate from delivery mode.

    Args:
        mode: Negotiated response mode.
        service: Injected data service.

    Returns:
        Response in appropriate mode.
    """
    if mode == ResponseMode.STREAM:
        async def stream_products() -> AsyncGenerator[str, None]:
            async for product in service.get_stream():
                yield f"data: {json.dumps(product)}\n\n"

        return StreamingResponse(
            stream_products(),
            media_type="text/event-stream",
        )

    products = await service.get_batch()
    return JSONResponse({"products": products})


# Demo function
async def demo() -> None:
    """Demonstrate mode detection patterns."""
    print("=== Mode Detection Example ===\n")

    # Simulate different request scenarios
    print("1. Simulating Accept Header Detection:")
    print("-" * 40)

    # Create mock requests
    from unittest.mock import MagicMock

    # Request with JSON accept header
    json_request = MagicMock()
    json_request.headers = {"accept": "application/json"}
    mode = detect_response_mode(json_request)
    print(f"  Accept: application/json -> Mode: {mode.value}")

    # Request with SSE accept header
    sse_request = MagicMock()
    sse_request.headers = {"accept": "text/event-stream"}
    mode = detect_response_mode(sse_request)
    print(f"  Accept: text/event-stream -> Mode: {mode.value}")

    # Request with multiple types (prefers streaming if present)
    multi_request = MagicMock()
    multi_request.headers = {"accept": "text/event-stream, application/json"}
    mode = detect_response_mode(multi_request)
    print(f"  Accept: text/event-stream, application/json -> Mode: {mode.value}")

    print("\n2. DataService Demonstration:")
    print("-" * 40)

    service = DataService()

    print("  Batch mode:")
    batch_data = await service.get_batch()
    for item in batch_data:
        print(f"    {item}")

    print("\n  Stream mode:")
    async for item in service.get_stream():
        print(f"    Streamed: {item}")

    print("\n3. Mode Negotiation Priority:")
    print("-" * 40)
    print("  Priority order:")
    print("    1. Explicit 'stream=true/false' query param")
    print("    2. 'format=stream/batch/auto' query param")
    print("    3. Accept header detection")
    print("    4. Default to BATCH")

    print("\n=== Example Complete ===")
    print("\nTo test with real HTTP requests, run:")
    print("  uvicorn dual_mode_streaming.examples.example_2_mode_detection:app")
    print("\nThen try:")
    print("  curl localhost:8000/items/simple?stream=false  # Batch")
    print("  curl localhost:8000/items/simple?stream=true   # Stream")
    print("  curl -H 'Accept: text/event-stream' localhost:8000/items/header")


if __name__ == "__main__":
    asyncio.run(demo())

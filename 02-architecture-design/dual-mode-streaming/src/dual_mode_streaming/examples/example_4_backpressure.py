"""Example 4: Backpressure and Flow Control.

This example demonstrates handling slow consumers, client disconnection,
and implementing flow control mechanisms in streaming responses.

Run with: make example-4
Or: uv run python -m dual_mode_streaming.examples.example_4_backpressure
"""

import asyncio
import json
import logging
from asyncio import Queue, Semaphore
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Backpressure Handling Example")


# Pattern 1: Client Disconnection Detection
async def disconnection_aware_generator(
    request: Request,
    total_items: int = 100,
) -> AsyncGenerator[str, None]:
    """Generator that stops when client disconnects.

    Args:
        request: FastAPI request for disconnection checking.
        total_items: Number of items to potentially generate.

    Yields:
        SSE-formatted data chunks.
    """
    for i in range(total_items):
        # Check if client is still connected
        if await request.is_disconnected():
            logger.info(f"Client disconnected at item {i}")
            break

        data = {"item": i, "timestamp": asyncio.get_event_loop().time()}
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.1)

    logger.info("Stream completed or client disconnected")


@app.get("/stream/aware")
async def disconnection_aware_stream(request: Request):
    """Stream that gracefully handles client disconnection.

    Args:
        request: The incoming request.

    Returns:
        StreamingResponse that stops on disconnect.
    """
    return StreamingResponse(
        disconnection_aware_generator(request),
        media_type="text/event-stream",
    )


# Pattern 2: Bounded Queue for Backpressure
class BoundedStreamProducer:
    """Producer that respects consumer pace via bounded queue."""

    def __init__(self, max_pending: int = 10) -> None:
        """Initialize with maximum pending items.

        Args:
            max_pending: Maximum items to buffer before blocking.
        """
        self.queue: Queue[dict | None] = Queue(maxsize=max_pending)
        self.max_pending = max_pending

    async def produce(self, total_items: int = 50) -> None:
        """Produce items into the bounded queue.

        This will block when queue is full, naturally applying backpressure.

        Args:
            total_items: Number of items to produce.
        """
        for i in range(total_items):
            item = {"id": i, "data": f"Item {i}"}
            logger.info(f"Producing item {i}, queue size: {self.queue.qsize()}")

            # This blocks when queue is full
            await self.queue.put(item)
            await asyncio.sleep(0.01)  # Fast production

        # Signal completion
        await self.queue.put(None)

    async def consume(self) -> AsyncGenerator[str, None]:
        """Consume items from queue as SSE events.

        Yields:
            SSE-formatted items from queue.
        """
        while True:
            item = await self.queue.get()
            if item is None:
                logger.info("Consumer received completion signal")
                break

            # Simulate slow consumer
            await asyncio.sleep(0.2)
            yield f"data: {json.dumps(item)}\n\n"


@app.get("/stream/bounded")
async def bounded_queue_stream():
    """Stream using bounded queue for backpressure.

    Returns:
        StreamingResponse with backpressure handling.
    """
    producer = BoundedStreamProducer(max_pending=5)

    async def generate() -> AsyncGenerator[str, None]:
        # Start producer in background
        producer_task = asyncio.create_task(producer.produce(20))

        try:
            async for chunk in producer.consume():
                yield chunk
        finally:
            producer_task.cancel()
            try:
                await producer_task
            except asyncio.CancelledError:
                pass

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


# Pattern 3: Semaphore-based Concurrency Control
async def rate_limited_generator(
    max_concurrent: int = 3,
) -> AsyncGenerator[str, None]:
    """Generator with semaphore-controlled concurrency.

    Args:
        max_concurrent: Maximum concurrent processing operations.

    Yields:
        SSE-formatted processed items.
    """
    semaphore = Semaphore(max_concurrent)
    items = list(range(15))

    async def process_item(item: int) -> dict:
        """Simulate expensive processing with concurrency limit."""
        async with semaphore:
            logger.info(f"Processing item {item}")
            await asyncio.sleep(0.3)  # Simulate work
            return {"id": item, "result": item * 2}

    # Process items with controlled concurrency
    for item in items:
        result = await process_item(item)
        yield f"data: {json.dumps(result)}\n\n"


@app.get("/stream/rate-limited")
async def rate_limited_stream():
    """Stream with rate-limited processing.

    Returns:
        StreamingResponse with concurrency control.
    """
    return StreamingResponse(
        rate_limited_generator(max_concurrent=2),
        media_type="text/event-stream",
    )


# Pattern 4: Graceful Cleanup on Cancellation
async def cleanup_aware_generator() -> AsyncGenerator[str, None]:
    """Generator with proper cleanup on cancellation.

    Yields:
        SSE-formatted items with cleanup on cancel.
    """
    resource_acquired = False

    try:
        # Simulate resource acquisition
        resource_acquired = True
        logger.info("Resource acquired")

        for i in range(50):
            data = {"item": i, "status": "processing"}
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.2)

    except asyncio.CancelledError:
        logger.info("Stream cancelled, performing cleanup...")
        raise

    finally:
        if resource_acquired:
            # Always cleanup resources
            logger.info("Releasing resource")
            await asyncio.sleep(0.1)  # Simulate cleanup
            logger.info("Resource released")


@app.get("/stream/cleanup")
async def cleanup_stream():
    """Stream with proper cleanup handling.

    Returns:
        StreamingResponse with cleanup on disconnect.
    """
    return StreamingResponse(
        cleanup_aware_generator(),
        media_type="text/event-stream",
    )


# Pattern 5: Timeout-based Flow Control
async def timeout_controlled_generator(
    item_timeout: float = 1.0,
) -> AsyncGenerator[str, None]:
    """Generator that times out slow operations.

    Args:
        item_timeout: Maximum time to wait for each item.

    Yields:
        SSE-formatted items with timeout handling.
    """
    async def fetch_item(item_id: int) -> dict | None:
        """Simulate fetching an item that might be slow."""
        # Some items are slow
        delay = 0.1 if item_id % 3 != 0 else 2.0
        await asyncio.sleep(delay)
        return {"id": item_id, "data": f"fetched-{item_id}"}

    for i in range(10):
        try:
            result = await asyncio.wait_for(
                fetch_item(i),
                timeout=item_timeout,
            )
            yield f"data: {json.dumps(result)}\n\n"
        except asyncio.TimeoutError:
            error_data = {"id": i, "error": "timeout", "skipped": True}
            yield f"event: timeout\ndata: {json.dumps(error_data)}\n\n"
            logger.warning(f"Timeout fetching item {i}")


@app.get("/stream/timeout")
async def timeout_stream():
    """Stream with per-item timeout handling.

    Returns:
        StreamingResponse with timeout protection.
    """
    return StreamingResponse(
        timeout_controlled_generator(item_timeout=0.5),
        media_type="text/event-stream",
    )


# Demo function
async def demo() -> None:
    """Demonstrate backpressure patterns."""
    print("=== Backpressure Handling Example ===\n")

    print("1. Bounded Queue Demonstration:")
    print("-" * 40)

    producer = BoundedStreamProducer(max_pending=3)
    produce_task = asyncio.create_task(producer.produce(10))

    items_consumed = 0
    async for chunk in producer.consume():
        if chunk.startswith("data: "):
            data = json.loads(chunk[6:])
            items_consumed += 1
            print(f"  Consumed: {data}")

    await produce_task
    print(f"  Total items consumed: {items_consumed}")

    print("\n2. Rate-Limited Processing:")
    print("-" * 40)
    count = 0
    async for chunk in rate_limited_generator(max_concurrent=2):
        if chunk.startswith("data: "):
            data = json.loads(chunk[6:])
            count += 1
            print(f"  Processed: {data}")
            if count >= 5:
                print("  ... (showing first 5)")
                break

    print("\n3. Timeout Handling:")
    print("-" * 40)
    async for chunk in timeout_controlled_generator(item_timeout=0.5):
        lines = chunk.strip().split("\n")
        event_type = "data"
        data_line = ""
        for line in lines:
            if line.startswith("event: "):
                event_type = line[7:]
            elif line.startswith("data: "):
                data_line = line[6:]

        if data_line:
            data = json.loads(data_line)
            status = "TIMEOUT" if event_type == "timeout" else "OK"
            print(f"  Item {data.get('id')}: {status}")

    print("\n=== Example Complete ===")
    print("\nTo test with real HTTP requests, run:")
    print("  uvicorn dual_mode_streaming.examples.example_4_backpressure:app")
    print("\nThen try:")
    print("  curl localhost:8000/stream/timeout")
    print("  curl localhost:8000/stream/bounded")
    print("  # Press Ctrl+C during stream to test cleanup")
    print("  curl localhost:8000/stream/cleanup")


if __name__ == "__main__":
    asyncio.run(demo())

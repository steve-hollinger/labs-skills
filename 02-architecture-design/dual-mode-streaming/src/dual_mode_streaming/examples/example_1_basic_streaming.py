"""Example 1: Basic SSE Streaming.

This example demonstrates fundamental Server-Sent Events (SSE) streaming
with FastAPI, including proper event formatting and response configuration.

Run with: make example-1
Or: uv run python -m dual_mode_streaming.examples.example_1_basic_streaming
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="Basic Streaming Example")


async def simple_number_generator() -> AsyncGenerator[str, None]:
    """Generate numbers 1-10 as SSE events.

    Yields:
        SSE-formatted strings with number data.
    """
    for i in range(1, 11):
        # Format as proper SSE event
        data = {"number": i, "squared": i**2}
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.3)  # Simulate processing time


@app.get("/stream/numbers")
async def stream_numbers() -> StreamingResponse:
    """Stream numbers 1-10 as SSE events.

    Returns:
        StreamingResponse with SSE content type.
    """
    return StreamingResponse(
        simple_number_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


async def event_with_metadata_generator() -> AsyncGenerator[str, None]:
    """Generate events with full SSE metadata.

    Demonstrates using event types and IDs for richer SSE streams.

    Yields:
        SSE-formatted strings with event metadata.
    """
    events = [
        {"type": "start", "message": "Stream starting"},
        {"type": "data", "value": 100},
        {"type": "data", "value": 200},
        {"type": "data", "value": 300},
        {"type": "end", "message": "Stream complete"},
    ]

    for i, event in enumerate(events):
        # Full SSE format with event type and ID
        lines = [
            f"id: {i + 1}",
            f"event: {event['type']}",
            f"data: {json.dumps(event)}",
            "",  # Empty line ends the event
        ]
        yield "\n".join(lines) + "\n"
        await asyncio.sleep(0.5)


@app.get("/stream/events")
async def stream_events() -> StreamingResponse:
    """Stream events with metadata (id, event type).

    Returns:
        StreamingResponse with typed SSE events.
    """
    return StreamingResponse(
        event_with_metadata_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


async def countdown_generator(start: int = 10) -> AsyncGenerator[str, None]:
    """Generate countdown events.

    Args:
        start: Number to count down from.

    Yields:
        SSE-formatted countdown events.
    """
    for i in range(start, 0, -1):
        data = {"countdown": i, "remaining_seconds": i}
        yield f"event: tick\ndata: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

    yield f"event: complete\ndata: {json.dumps({'message': 'Countdown complete!'})}\n\n"


@app.get("/stream/countdown/{start}")
async def stream_countdown(start: int = 10) -> StreamingResponse:
    """Stream a countdown from the specified number.

    Args:
        start: Number to count down from (default 10).

    Returns:
        StreamingResponse with countdown events.
    """
    return StreamingResponse(
        countdown_generator(start),
        media_type="text/event-stream",
    )


# Demo function to run without server
async def demo() -> None:
    """Demonstrate the streaming generators."""
    print("=== Basic Streaming Example ===\n")

    print("1. Simple Number Stream:")
    print("-" * 40)
    async for event in simple_number_generator():
        # Parse and display the SSE data
        if event.startswith("data: "):
            data = json.loads(event[6:].strip())
            print(f"  Received: {data}")

    print("\n2. Events with Metadata:")
    print("-" * 40)
    async for event in event_with_metadata_generator():
        lines = event.strip().split("\n")
        event_dict = {}
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                event_dict[key] = value
        if "data" in event_dict:
            print(f"  Event Type: {event_dict.get('event', 'message')}")
            print(f"  ID: {event_dict.get('id', 'none')}")
            print(f"  Data: {event_dict['data']}")
            print()

    print("3. Countdown Stream (5 seconds):")
    print("-" * 40)
    async for event in countdown_generator(5):
        if "data: " in event:
            data_line = [l for l in event.split("\n") if l.startswith("data: ")][0]
            data = json.loads(data_line[6:])
            if "countdown" in data:
                print(f"  {data['countdown']}...")
            else:
                print(f"  {data['message']}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(demo())

"""
Example 1: Basic SSE Endpoint

This example demonstrates the fundamentals of Server-Sent Events:
- SSE message format
- FastAPI StreamingResponse
- Generator functions for SSE
- Proper headers

Run this example to start a server, then test with curl or browser.
"""

import asyncio
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI(title="Basic SSE Example")


# ============================================================================
# SSE Generators
# ============================================================================

async def simple_message_generator():
    """
    Generate simple SSE messages.

    SSE Format:
    - Each message starts with "data: " followed by the content
    - Messages are separated by double newlines (\\n\\n)
    """
    messages = [
        "Hello, World!",
        "This is a Server-Sent Event.",
        "Messages stream one at a time.",
        "Each message is sent as a separate event.",
        "Stream complete!",
    ]

    for msg in messages:
        # Format: data: <content>\n\n
        yield f"data: {msg}\n\n"
        await asyncio.sleep(0.5)

    # Signal completion
    yield "data: [DONE]\n\n"


async def json_data_generator():
    """
    Generate SSE messages with JSON data.

    JSON is the common format for structured SSE data.
    """
    for i in range(10):
        data = {
            "id": i,
            "timestamp": datetime.now().isoformat(),
            "value": i * 10,
            "message": f"Update #{i}"
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.3)

    yield "data: [DONE]\n\n"


async def custom_events_generator():
    """
    Generate SSE messages with custom event types.

    The 'event:' field allows clients to listen for specific events.
    """
    # Start event
    yield f"event: start\ndata: {json.dumps({'status': 'starting'})}\n\n"
    await asyncio.sleep(0.5)

    # Progress events
    for i in range(5):
        progress = {
            "step": i + 1,
            "total": 5,
            "percent": (i + 1) * 20
        }
        yield f"event: progress\ndata: {json.dumps(progress)}\n\n"
        await asyncio.sleep(0.3)

    # Complete event
    yield f"event: complete\ndata: {json.dumps({'status': 'done', 'message': 'All steps finished!'})}\n\n"


async def numbered_events_generator():
    """
    Generate SSE messages with IDs for reconnection support.

    The 'id:' field enables clients to resume from the last received event.
    """
    for i in range(10):
        event_id = f"evt-{i:04d}"
        data = {"sequence": i, "data": f"Event {i}"}

        # Format: id + event + data
        yield f"id: {event_id}\ndata: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.3)

    yield "data: [DONE]\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/simple")
async def simple_stream():
    """Basic text message stream."""
    return StreamingResponse(
        simple_message_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/json")
async def json_stream():
    """JSON data stream."""
    return StreamingResponse(
        json_data_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/events")
async def custom_events_stream():
    """Stream with custom event types."""
    return StreamingResponse(
        custom_events_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/numbered")
async def numbered_stream():
    """Stream with event IDs for reconnection."""
    return StreamingResponse(
        numbered_events_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/")
async def info():
    """API info."""
    return {
        "example": "Basic SSE",
        "endpoints": {
            "/simple": "Simple text messages",
            "/json": "JSON data stream",
            "/events": "Custom event types",
            "/numbered": "Events with IDs"
        },
        "test_with": "curl -N http://localhost:8001/simple"
    }


# ============================================================================
# Main
# ============================================================================

def demonstrate_sse_format():
    """Show SSE message format examples."""
    print("=" * 60)
    print("Example 1: Basic SSE")
    print("=" * 60)

    print("\n--- SSE Message Format ---")
    print("Simple message:")
    print('  data: Hello, World!\\n\\n')

    print("\nJSON message:")
    print('  data: {"id": 1, "value": "test"}\\n\\n')

    print("\nCustom event:")
    print('  event: progress')
    print('  data: {"percent": 50}\\n\\n')

    print("\nMessage with ID:")
    print('  id: evt-0001')
    print('  data: {"sequence": 1}\\n\\n')

    print("\nMultiple data lines (concatenated with newlines):")
    print('  data: Line 1')
    print('  data: Line 2')
    print('  data: Line 3\\n\\n')

    print("\nComment (keepalive):")
    print('  : this is a comment\\n\\n')

    print("\n--- Key Points ---")
    print("1. Content-Type must be 'text/event-stream'")
    print("2. Messages end with double newline (\\n\\n)")
    print("3. Use 'data:' for message content")
    print("4. Use 'event:' for custom event types")
    print("5. Use 'id:' for reconnection support")
    print("6. Use ':' for comments/keepalive")


def main():
    """Run the example."""
    demonstrate_sse_format()

    print("\n" + "=" * 60)
    print("Starting SSE server on http://localhost:8001")
    print("=" * 60)
    print("\nTest endpoints:")
    print("  curl -N http://localhost:8001/simple")
    print("  curl -N http://localhost:8001/json")
    print("  curl -N http://localhost:8001/events")
    print("  curl -N http://localhost:8001/numbered")
    print("\nPress Ctrl+C to stop")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


if __name__ == "__main__":
    main()

"""
Example 3: Client Consumption

This example demonstrates consuming SSE streams from Python clients:
- Synchronous consumption with httpx
- Asynchronous consumption with httpx
- Parsing different event types
- Error handling and reconnection

This example requires a running server (examples 1 or 2).
"""

import json
import asyncio
import httpx
from typing import Generator, AsyncGenerator


# ============================================================================
# Synchronous Client
# ============================================================================

def consume_sse_sync(url: str) -> Generator[dict, None, None]:
    """
    Consume SSE stream synchronously.

    Args:
        url: The SSE endpoint URL

    Yields:
        Parsed event data
    """
    print(f"Connecting to: {url}")

    with httpx.stream("GET", url, timeout=60.0) as response:
        response.raise_for_status()
        print(f"Connected! Status: {response.status_code}")

        for line in response.iter_lines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("data: "):
                data = line[6:]

                if data == "[DONE]":
                    print("Received [DONE] marker")
                    break

                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    yield {"raw": data}

            elif line.startswith("event: "):
                event_type = line[7:]
                print(f"  [Event type: {event_type}]")

            elif line.startswith(":"):
                # Comment/keepalive
                pass


def collect_stream_content(url: str) -> str:
    """Collect streaming content into a single string."""
    content_parts = []

    for event in consume_sse_sync(url):
        if "content" in event:
            content_parts.append(event["content"])
        elif "message" in event:
            content_parts.append(event["message"])

    return "".join(content_parts)


# ============================================================================
# Asynchronous Client
# ============================================================================

async def consume_sse_async(url: str) -> AsyncGenerator[dict, None]:
    """
    Consume SSE stream asynchronously.

    Args:
        url: The SSE endpoint URL

    Yields:
        Parsed event data
    """
    print(f"Async connecting to: {url}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            print(f"Connected! Status: {response.status_code}")

            async for line in response.aiter_lines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        print("Received [DONE] marker")
                        break

                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield {"raw": data}


async def collect_stream_content_async(url: str) -> str:
    """Collect streaming content asynchronously."""
    content_parts = []

    async for event in consume_sse_async(url):
        if "content" in event:
            content_parts.append(event["content"])

    return "".join(content_parts)


# ============================================================================
# Advanced Consumption Patterns
# ============================================================================

async def consume_with_callbacks(
    url: str,
    on_content=None,
    on_metadata=None,
    on_error=None
):
    """
    Consume SSE with callback handlers.

    Args:
        url: The SSE endpoint URL
        on_content: Callback for content events
        on_metadata: Callback for metadata events
        on_error: Callback for error events
    """
    current_event_type = "message"

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("event: "):
                    current_event_type = line[7:]

                elif line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        parsed = json.loads(data)
                    except json.JSONDecodeError:
                        parsed = {"raw": data}

                    # Route to appropriate callback
                    if current_event_type == "error" and on_error:
                        on_error(parsed)
                    elif current_event_type == "metadata" and on_metadata:
                        on_metadata(parsed)
                    elif on_content:
                        on_content(parsed)

                    current_event_type = "message"


async def consume_with_retry(
    url: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> AsyncGenerator[dict, None]:
    """
    Consume SSE with automatic retry on failure.

    Args:
        url: The SSE endpoint URL
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Yields:
        Parsed event data
    """
    retries = 0

    while retries <= max_retries:
        try:
            async for event in consume_sse_async(url):
                retries = 0  # Reset on successful data
                yield event
            break  # Stream completed normally

        except (httpx.HTTPError, httpx.StreamClosed) as e:
            retries += 1
            if retries > max_retries:
                print(f"Max retries exceeded: {e}")
                raise

            print(f"Connection error, retry {retries}/{max_retries}: {e}")
            await asyncio.sleep(retry_delay * retries)


# ============================================================================
# Demonstration
# ============================================================================

def demo_sync_consumption():
    """Demonstrate synchronous SSE consumption."""
    print("\n--- Synchronous Consumption ---")

    url = "http://localhost:8000/stream?count=5&delay=0.2"

    try:
        for event in consume_sse_sync(url):
            print(f"  Received: {event}")
    except httpx.ConnectError:
        print("  Error: Could not connect. Is the server running?")
        print("  Start with: make run-server")


async def demo_async_consumption():
    """Demonstrate asynchronous SSE consumption."""
    print("\n--- Asynchronous Consumption ---")

    url = "http://localhost:8000/stream?count=5&delay=0.2"

    try:
        async for event in consume_sse_async(url):
            print(f"  Received: {event}")
    except httpx.ConnectError:
        print("  Error: Could not connect. Is the server running?")


async def demo_chat_streaming():
    """Demonstrate chat endpoint consumption."""
    print("\n--- Chat Streaming ---")

    url = "http://localhost:8000/chat?prompt=Hello"

    print("Streaming response: ", end="")
    try:
        async for event in consume_sse_async(url):
            if "content" in event:
                print(event["content"], end="", flush=True)
        print()
    except httpx.ConnectError:
        print("\n  Error: Could not connect. Is the server running?")


async def demo_callback_consumption():
    """Demonstrate callback-based consumption."""
    print("\n--- Callback-Based Consumption ---")

    collected = []

    def on_content(data):
        if "content" in data:
            collected.append(data["content"])
            print(data["content"], end="", flush=True)

    def on_metadata(data):
        print(f"\n  [Metadata: {data}]")

    def on_error(data):
        print(f"\n  [Error: {data}]")

    url = "http://localhost:8000/chat?prompt=Count+to+5"

    try:
        await consume_with_callbacks(
            url,
            on_content=on_content,
            on_metadata=on_metadata,
            on_error=on_error
        )
        print(f"\n  Total collected: {''.join(collected)}")
    except httpx.ConnectError:
        print("  Error: Could not connect.")


def main():
    """Run client consumption examples."""
    print("=" * 60)
    print("Example 3: Client Consumption")
    print("=" * 60)
    print("\nNote: This requires a running server.")
    print("Start with: make run-server")
    print("=" * 60)

    # Sync demo
    demo_sync_consumption()

    # Async demos
    asyncio.run(demo_async_consumption())
    asyncio.run(demo_chat_streaming())
    asyncio.run(demo_callback_consumption())

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Use httpx.stream() for consuming SSE")
    print("2. Parse 'data: ' lines and handle [DONE]")
    print("3. Track 'event: ' lines for custom event types")
    print("4. Implement retry logic for production use")
    print("5. Use callbacks for complex event handling")
    print("=" * 60)


if __name__ == "__main__":
    main()

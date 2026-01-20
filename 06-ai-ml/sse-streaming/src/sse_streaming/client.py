"""
SSE Client

Python client for consuming Server-Sent Events.
"""

import json
import httpx
from typing import AsyncGenerator, Generator


def consume_sse_sync(
    url: str,
    timeout: float | None = None
) -> Generator[dict, None, None]:
    """
    Consume SSE stream synchronously.

    Args:
        url: The SSE endpoint URL
        timeout: Optional timeout in seconds

    Yields:
        Parsed JSON data from each event
    """
    with httpx.stream("GET", url, timeout=timeout) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix

                if data == "[DONE]":
                    break

                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    yield {"raw": data}

            elif line.startswith("event: "):
                # Custom event type - could be handled separately
                pass

            elif line.startswith(":"):
                # Comment/keepalive - ignore
                pass


async def consume_sse_async(
    url: str,
    timeout: float | None = None
) -> AsyncGenerator[dict, None]:
    """
    Consume SSE stream asynchronously.

    Args:
        url: The SSE endpoint URL
        timeout: Optional timeout in seconds

    Yields:
        Parsed JSON data from each event
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                line = line.strip()

                if not line:
                    continue

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield {"raw": data}


class SSEClient:
    """
    A reusable SSE client with connection management.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def stream(self, endpoint: str, **params) -> Generator[dict, None, None]:
        """Stream from an endpoint synchronously."""
        url = f"{self.base_url}{endpoint}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        yield from consume_sse_sync(url)

    async def stream_async(self, endpoint: str, **params) -> AsyncGenerator[dict, None]:
        """Stream from an endpoint asynchronously."""
        url = f"{self.base_url}{endpoint}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        async for item in consume_sse_async(url):
            yield item


def main():
    """Test the SSE client against the local server."""
    print("SSE Client Test")
    print("=" * 50)
    print("Make sure the server is running: make run-server")
    print("=" * 50)

    client = SSEClient()

    # Test basic stream
    print("\n--- Testing Basic Stream ---")
    try:
        for i, event in enumerate(client.stream("/stream", count=5, delay=0.2)):
            print(f"Event {i}: {event}")
    except httpx.ConnectError:
        print("Error: Could not connect to server.")
        print("Start the server with: make run-server")
        return

    # Test chat stream
    print("\n--- Testing Chat Stream ---")
    print("Prompt: 'Hello'")
    print("Response: ", end="")

    for event in client.stream("/chat", prompt="Hello"):
        if "content" in event:
            print(event["content"], end="", flush=True)

    print("\n")
    print("=" * 50)
    print("Client test complete!")


if __name__ == "__main__":
    main()

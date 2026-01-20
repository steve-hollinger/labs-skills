"""Streaming utilities for SSE responses."""

import json
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, TypeVar

from fastapi.responses import StreamingResponse

T = TypeVar("T")


@dataclass
class SSEEvent:
    """Server-Sent Event structure.

    Attributes:
        data: The event payload (will be JSON serialized if dict/list).
        event: Optional event type name.
        id: Optional event ID for reconnection support.
        retry: Optional retry interval in milliseconds.
    """

    data: Any
    event: str | None = None
    id: str | None = None
    retry: int | None = None
    _custom_fields: dict[str, str] = field(default_factory=dict)

    def format(self) -> str:
        """Format the event as an SSE message string.

        Returns:
            Properly formatted SSE message with trailing double newline.
        """
        lines: list[str] = []

        if self.event:
            lines.append(f"event: {self.event}")

        if self.id:
            lines.append(f"id: {self.id}")

        if self.retry is not None:
            lines.append(f"retry: {self.retry}")

        # Add custom fields
        for key, value in self._custom_fields.items():
            lines.append(f"{key}: {value}")

        # Format data - JSON serialize if needed
        if isinstance(self.data, (dict, list)):
            data_str = json.dumps(self.data)
        else:
            data_str = str(self.data)

        # Handle multi-line data
        for line in data_str.split("\n"):
            lines.append(f"data: {line}")

        return "\n".join(lines) + "\n\n"


def format_sse_event(
    data: Any,
    event: str | None = None,
    id: str | None = None,
    retry: int | None = None,
) -> str:
    """Format data as an SSE event string.

    Args:
        data: The payload to send (dict/list will be JSON serialized).
        event: Optional event type name.
        id: Optional event ID for reconnection.
        retry: Optional retry interval in milliseconds.

    Returns:
        Formatted SSE message string.
    """
    sse = SSEEvent(data=data, event=event, id=id, retry=retry)
    return sse.format()


def format_sse_data(data: Any) -> str:
    """Simple SSE data formatting without event metadata.

    Args:
        data: The payload to send.

    Returns:
        Formatted SSE data line with trailing double newline.
    """
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data)
    else:
        data_str = str(data)
    return f"data: {data_str}\n\n"


def create_streaming_response(
    generator: AsyncGenerator[str, None],
    headers: dict[str, str] | None = None,
) -> StreamingResponse:
    """Create a properly configured SSE streaming response.

    Args:
        generator: Async generator yielding SSE-formatted strings.
        headers: Optional additional headers to include.

    Returns:
        Configured StreamingResponse for SSE.
    """
    default_headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disable nginx buffering
    }

    if headers:
        default_headers.update(headers)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers=default_headers,
    )


async def transform_stream(
    source: AsyncGenerator[T, None],
    transformer: Callable[[T], str],
) -> AsyncGenerator[str, None]:
    """Transform a source generator into SSE-formatted output.

    Args:
        source: Source async generator producing items.
        transformer: Function to convert items to SSE strings.

    Yields:
        SSE-formatted strings from transformed items.
    """
    async for item in source:
        yield transformer(item)


async def batch_to_stream(
    items: list[T],
    formatter: Callable[[T], str] | None = None,
    delay: float = 0.0,
) -> AsyncGenerator[str, None]:
    """Convert a batch of items into a simulated stream.

    Useful for testing streaming clients with known data.

    Args:
        items: List of items to stream.
        formatter: Optional formatter function (defaults to format_sse_data).
        delay: Optional delay between items in seconds.

    Yields:
        SSE-formatted strings for each item.
    """
    import asyncio

    format_fn = formatter or format_sse_data

    for item in items:
        yield format_fn(item)
        if delay > 0:
            await asyncio.sleep(delay)


class StreamBuffer:
    """Buffer for collecting streamed data into batches.

    Useful when you need to provide both modes but only have streaming source.
    """

    def __init__(self) -> None:
        """Initialize an empty buffer."""
        self._items: list[Any] = []

    async def collect(self, source: AsyncGenerator[Any, None]) -> list[Any]:
        """Collect all items from a source generator.

        Args:
            source: Async generator to collect from.

        Returns:
            List of all collected items.
        """
        self._items = []
        async for item in source:
            self._items.append(item)
        return self._items

    @property
    def items(self) -> list[Any]:
        """Get the collected items."""
        return self._items


async def resilient_stream(
    source: AsyncGenerator[T, None],
    on_error: Callable[[Exception], str] | None = None,
    on_complete: Callable[[], str] | None = None,
) -> AsyncGenerator[str, None]:
    """Wrap a stream with error handling and completion events.

    Args:
        source: Source async generator.
        on_error: Optional error handler returning SSE string.
        on_complete: Optional completion handler returning SSE string.

    Yields:
        SSE-formatted strings with error handling.
    """
    try:
        async for item in source:
            if isinstance(item, str):
                yield item
            else:
                yield format_sse_data(item)
    except Exception as e:
        if on_error:
            yield on_error(e)
        else:
            error_event = format_sse_event(
                data={"error": str(e), "type": type(e).__name__},
                event="error",
            )
            yield error_event
    finally:
        if on_complete:
            yield on_complete()

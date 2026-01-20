"""Tests for streaming utilities."""

import json
import pytest

from dual_mode_streaming.streaming import (
    SSEEvent,
    format_sse_event,
    format_sse_data,
    batch_to_stream,
    StreamBuffer,
)


class TestSSEEvent:
    """Tests for SSEEvent class."""

    def test_basic_data_format(self) -> None:
        """Test formatting basic data-only event."""
        event = SSEEvent(data={"message": "hello"})
        formatted = event.format()

        assert formatted.startswith("data: ")
        assert formatted.endswith("\n\n")
        assert '"message": "hello"' in formatted

    def test_data_with_event_type(self) -> None:
        """Test formatting event with type."""
        event = SSEEvent(data="test", event="custom")
        formatted = event.format()

        assert "event: custom\n" in formatted
        assert "data: test\n" in formatted

    def test_data_with_id(self) -> None:
        """Test formatting event with ID."""
        event = SSEEvent(data="test", id="123")
        formatted = event.format()

        assert "id: 123\n" in formatted

    def test_data_with_retry(self) -> None:
        """Test formatting event with retry interval."""
        event = SSEEvent(data="test", retry=5000)
        formatted = event.format()

        assert "retry: 5000\n" in formatted

    def test_full_event_format(self) -> None:
        """Test formatting event with all fields."""
        event = SSEEvent(
            data={"status": "ok"},
            event="status",
            id="msg-1",
            retry=3000,
        )
        formatted = event.format()

        assert "event: status\n" in formatted
        assert "id: msg-1\n" in formatted
        assert "retry: 3000\n" in formatted
        assert "data: " in formatted

    def test_string_data(self) -> None:
        """Test formatting with string data."""
        event = SSEEvent(data="plain text")
        formatted = event.format()

        assert "data: plain text\n\n" in formatted

    def test_list_data_serialization(self) -> None:
        """Test that lists are JSON serialized."""
        event = SSEEvent(data=[1, 2, 3])
        formatted = event.format()

        assert "data: [1, 2, 3]\n\n" in formatted


class TestFormatSSEEvent:
    """Tests for format_sse_event function."""

    def test_basic_format(self) -> None:
        """Test basic event formatting."""
        result = format_sse_event({"key": "value"})

        assert result.startswith("data: ")
        assert result.endswith("\n\n")

    def test_with_event_type(self) -> None:
        """Test formatting with event type."""
        result = format_sse_event("data", event="update")

        assert "event: update\n" in result

    def test_with_id_and_retry(self) -> None:
        """Test formatting with id and retry."""
        result = format_sse_event("data", id="1", retry=1000)

        assert "id: 1\n" in result
        assert "retry: 1000\n" in result


class TestFormatSSEData:
    """Tests for format_sse_data function."""

    def test_dict_data(self) -> None:
        """Test formatting dictionary data."""
        result = format_sse_data({"foo": "bar"})

        assert result == 'data: {"foo": "bar"}\n\n'

    def test_string_data(self) -> None:
        """Test formatting string data."""
        result = format_sse_data("hello world")

        assert result == "data: hello world\n\n"

    def test_integer_data(self) -> None:
        """Test formatting integer data."""
        result = format_sse_data(42)

        assert result == "data: 42\n\n"


class TestBatchToStream:
    """Tests for batch_to_stream function."""

    @pytest.mark.asyncio
    async def test_converts_list_to_stream(self) -> None:
        """Test converting a list to SSE stream."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        results = []

        async for chunk in batch_to_stream(items):
            results.append(chunk)

        assert len(results) == 3
        for i, chunk in enumerate(results, 1):
            assert f'"id": {i}' in chunk
            assert chunk.startswith("data: ")

    @pytest.mark.asyncio
    async def test_with_custom_formatter(self) -> None:
        """Test with custom formatter function."""
        items = [1, 2, 3]

        def custom_format(x: int) -> str:
            return f"event: number\ndata: {x}\n\n"

        results = []
        async for chunk in batch_to_stream(items, formatter=custom_format):
            results.append(chunk)

        assert all("event: number" in r for r in results)

    @pytest.mark.asyncio
    async def test_empty_list(self) -> None:
        """Test with empty list."""
        results = []
        async for chunk in batch_to_stream([]):
            results.append(chunk)

        assert len(results) == 0


class TestStreamBuffer:
    """Tests for StreamBuffer class."""

    @pytest.mark.asyncio
    async def test_collect_items(self) -> None:
        """Test collecting items from async generator."""
        async def source():
            for i in range(5):
                yield {"id": i}

        buffer = StreamBuffer()
        items = await buffer.collect(source())

        assert len(items) == 5
        assert items[0] == {"id": 0}
        assert items[4] == {"id": 4}

    @pytest.mark.asyncio
    async def test_items_property(self) -> None:
        """Test accessing collected items via property."""
        async def source():
            yield "a"
            yield "b"

        buffer = StreamBuffer()
        await buffer.collect(source())

        assert buffer.items == ["a", "b"]

    @pytest.mark.asyncio
    async def test_recollect_clears_previous(self) -> None:
        """Test that recollecting clears previous items."""
        async def source1():
            yield 1

        async def source2():
            yield 2
            yield 3

        buffer = StreamBuffer()
        await buffer.collect(source1())
        assert len(buffer.items) == 1

        await buffer.collect(source2())
        assert len(buffer.items) == 2
        assert buffer.items == [2, 3]

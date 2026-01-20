"""Tests demonstrating async generator testing with pytest-asyncio."""

import asyncio
from typing import AsyncGenerator

import pytest


# =============================================================================
# Async Generators to Test
# =============================================================================


async def number_stream(count: int) -> AsyncGenerator[int, None]:
    """Async generator that yields numbers."""
    for i in range(count):
        await asyncio.sleep(0.01)
        yield i


async def paginated_fetch(
    total_items: int, page_size: int
) -> AsyncGenerator[list[dict[str, int | str]], None]:
    """Simulate paginated API fetch."""
    for page in range(0, total_items, page_size):
        await asyncio.sleep(0.01)
        items = [
            {"id": i, "name": f"Item {i}"}
            for i in range(page, min(page + page_size, total_items))
        ]
        yield items


async def event_stream_with_error(
    event_count: int, fail_at: int | None = None
) -> AsyncGenerator[dict[str, int | str], None]:
    """Event stream that can fail at a specified event."""
    for i in range(event_count):
        if fail_at is not None and i == fail_at:
            raise ValueError(f"Stream error at event {i}")
        await asyncio.sleep(0.01)
        yield {"event_id": i, "data": f"Event data {i}"}


class AsyncIterableCollection:
    """Class implementing async iterator protocol."""

    def __init__(self, items: list[str]) -> None:
        self.items = items
        self._index = 0

    def __aiter__(self) -> "AsyncIterableCollection":
        self._index = 0  # Reset for re-iteration
        return self

    async def __anext__(self) -> str:
        if self._index >= len(self.items):
            raise StopAsyncIteration
        await asyncio.sleep(0.01)
        item = self.items[self._index]
        self._index += 1
        return item


# =============================================================================
# Basic Async Generator Tests
# =============================================================================


async def test_number_stream_basic() -> None:
    """Test basic async generator iteration."""
    results = []
    async for num in number_stream(5):
        results.append(num)

    assert results == [0, 1, 2, 3, 4]


async def test_number_stream_with_comprehension() -> None:
    """Test async generator with list comprehension."""
    results = [num async for num in number_stream(3)]
    assert results == [0, 1, 2]


async def test_number_stream_empty() -> None:
    """Test async generator with zero items."""
    results = [num async for num in number_stream(0)]
    assert results == []


async def test_number_stream_single_item() -> None:
    """Test async generator with single item."""
    results = [num async for num in number_stream(1)]
    assert results == [0]


# =============================================================================
# Early Termination Tests
# =============================================================================


async def test_early_break() -> None:
    """Test breaking out of async generator early."""
    results = []
    async for num in number_stream(100):
        results.append(num)
        if num >= 4:
            break

    assert results == [0, 1, 2, 3, 4]


async def test_find_first_match() -> None:
    """Test finding first matching item."""
    found = None
    async for num in number_stream(100):
        if num > 5:
            found = num
            break

    assert found == 6


async def test_break_with_else() -> None:
    """Test async for/else with break."""
    found = False
    async for num in number_stream(10):
        if num == 5:
            found = True
            break
    else:
        # This runs if we didn't break
        found = False

    assert found is True


async def test_no_break_else() -> None:
    """Test async for/else without break."""
    completed = False
    async for num in number_stream(3):
        pass
    else:
        # This runs when loop completes without break
        completed = True

    assert completed is True


# =============================================================================
# Paginated Results Tests
# =============================================================================


async def test_paginated_fetch_basic() -> None:
    """Test paginated async generator."""
    all_items: list[dict[str, int | str]] = []
    page_count = 0

    async for page in paginated_fetch(total_items=10, page_size=3):
        all_items.extend(page)
        page_count += 1

    assert len(all_items) == 10
    assert page_count == 4  # ceil(10/3) = 4 pages


async def test_paginated_fetch_exact_pages() -> None:
    """Test pagination with exact page boundaries."""
    all_items: list[dict[str, int | str]] = []

    async for page in paginated_fetch(total_items=9, page_size=3):
        all_items.extend(page)

    assert len(all_items) == 9


async def test_paginated_fetch_page_sizes() -> None:
    """Test that page sizes are correct."""
    page_sizes = []

    async for page in paginated_fetch(total_items=10, page_size=3):
        page_sizes.append(len(page))

    assert page_sizes == [3, 3, 3, 1]


async def test_paginated_fetch_content() -> None:
    """Test paginated content is correct."""
    all_items: list[dict[str, int | str]] = []

    async for page in paginated_fetch(total_items=5, page_size=2):
        all_items.extend(page)

    assert all_items[0]["id"] == 0
    assert all_items[-1]["id"] == 4
    ids = [item["id"] for item in all_items]
    assert ids == [0, 1, 2, 3, 4]


# =============================================================================
# Error Handling Tests
# =============================================================================


async def test_generator_error_raised() -> None:
    """Test async generator that raises error."""
    results = []

    with pytest.raises(ValueError, match="Stream error at event 2"):
        async for event in event_stream_with_error(5, fail_at=2):
            results.append(event)

    # Should have collected events before error
    assert len(results) == 2


async def test_generator_error_handling() -> None:
    """Test handling error from async generator."""
    results = []
    error_message = None

    try:
        async for event in event_stream_with_error(5, fail_at=3):
            results.append(event)
    except ValueError as e:
        error_message = str(e)

    assert len(results) == 3
    assert error_message == "Stream error at event 3"


async def test_generator_no_error() -> None:
    """Test async generator completes without error."""
    results = []

    async for event in event_stream_with_error(5, fail_at=None):
        results.append(event)

    assert len(results) == 5


# =============================================================================
# Async Iterator Protocol Tests
# =============================================================================


async def test_async_iterable_class() -> None:
    """Test class implementing async iterator protocol."""
    collection = AsyncIterableCollection(["a", "b", "c"])

    results = []
    async for item in collection:
        results.append(item)

    assert results == ["a", "b", "c"]


async def test_async_iterable_reuse() -> None:
    """Test that async iterable can be reused."""
    collection = AsyncIterableCollection(["x", "y"])

    # First iteration
    first = [item async for item in collection]

    # Second iteration (should work because __aiter__ resets index)
    second = [item async for item in collection]

    assert first == ["x", "y"]
    assert second == ["x", "y"]


async def test_anext_builtin() -> None:
    """Test using anext() builtin."""
    gen = number_stream(5)

    first = await anext(gen)
    second = await anext(gen)
    third = await anext(gen)

    assert first == 0
    assert second == 1
    assert third == 2


async def test_anext_with_default() -> None:
    """Test anext() with default value."""
    gen = number_stream(2)

    # Consume all items
    await anext(gen)  # 0
    await anext(gen)  # 1

    # Next call would raise StopAsyncIteration, but we provide default
    result = await anext(gen, -1)
    assert result == -1


async def test_anext_stop_iteration() -> None:
    """Test anext() raises StopAsyncIteration."""
    gen = number_stream(1)

    await anext(gen)  # 0

    with pytest.raises(StopAsyncIteration):
        await anext(gen)

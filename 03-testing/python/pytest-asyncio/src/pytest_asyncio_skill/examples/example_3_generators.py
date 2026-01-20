"""Example 3: Testing Async Generators

This example demonstrates how to test async generators and iterators,
including collecting results, early termination, and error handling.
"""

import asyncio
from typing import AsyncGenerator


async def number_stream(count: int) -> AsyncGenerator[int, None]:
    """Async generator that yields numbers."""
    for i in range(count):
        await asyncio.sleep(0.01)  # Simulate async work
        yield i


async def paginated_fetch(
    total_items: int, page_size: int
) -> AsyncGenerator[list[dict[str, int | str]], None]:
    """Simulate paginated API fetch."""
    for page in range(0, total_items, page_size):
        await asyncio.sleep(0.01)  # Simulate API call
        items = [
            {"id": i, "name": f"Item {i}"}
            for i in range(page, min(page + page_size, total_items))
        ]
        yield items


async def event_stream(
    event_count: int, fail_at: int | None = None
) -> AsyncGenerator[dict[str, int | str], None]:
    """Simulate an event stream with optional failure."""
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
        return self

    async def __anext__(self) -> str:
        if self._index >= len(self.items):
            raise StopAsyncIteration
        await asyncio.sleep(0.01)  # Simulate async work
        item = self.items[self._index]
        self._index += 1
        return item


def main() -> None:
    """Demonstrate testing async generators."""
    print("Example 3: Testing Async Generators")
    print("=" * 50)
    print()

    # Basic async generator testing
    print("1. Basic Async Generator Test")
    print("-" * 40)
    print("""
    async def test_number_stream():
        \"\"\"Test basic async generator.\"\"\"
        results = []
        async for num in number_stream(5):
            results.append(num)

        assert results == [0, 1, 2, 3, 4]


    async def test_with_list_comprehension():
        \"\"\"Collect async generator to list.\"\"\"
        results = [num async for num in number_stream(3)]
        assert results == [0, 1, 2]
    """)

    # Testing early termination
    print("2. Testing Early Termination")
    print("-" * 40)
    print("""
    async def test_early_break():
        \"\"\"Test breaking out of async generator early.\"\"\"
        results = []
        async for num in number_stream(100):
            results.append(num)
            if num >= 4:
                break

        assert results == [0, 1, 2, 3, 4]
        # Generator properly cleaned up after break


    async def test_find_first():
        \"\"\"Find first matching item in stream.\"\"\"
        async for num in number_stream(100):
            if num > 5:
                found = num
                break
        else:
            found = None

        assert found == 6
    """)

    # Testing paginated results
    print("3. Testing Paginated Results")
    print("-" * 40)
    print("""
    async def test_paginated_fetch():
        \"\"\"Test paginated async generator.\"\"\"
        all_items = []
        page_count = 0

        async for page in paginated_fetch(total_items=10, page_size=3):
            all_items.extend(page)
            page_count += 1

        assert len(all_items) == 10
        assert page_count == 4  # 3+3+3+1
        assert all_items[0]["id"] == 0
        assert all_items[-1]["id"] == 9
    """)

    # Testing error handling
    print("4. Testing Error Handling in Generators")
    print("-" * 40)
    print("""
    import pytest

    async def test_generator_error():
        \"\"\"Test async generator that raises error.\"\"\"
        results = []

        with pytest.raises(ValueError, match="Stream error at event 2"):
            async for event in event_stream(5, fail_at=2):
                results.append(event)

        # Collected events before error
        assert len(results) == 2


    async def test_handle_generator_error():
        \"\"\"Handle error and continue processing.\"\"\"
        results = []
        error_occurred = False

        try:
            async for event in event_stream(5, fail_at=2):
                results.append(event)
        except ValueError:
            error_occurred = True

        assert error_occurred
        assert len(results) == 2
    """)

    # Testing async iterator protocol
    print("5. Testing Async Iterator Protocol")
    print("-" * 40)
    print("""
    async def test_async_iterable_class():
        \"\"\"Test class implementing __aiter__ and __anext__.\"\"\"
        collection = AsyncIterableCollection(["a", "b", "c"])

        results = []
        async for item in collection:
            results.append(item)

        assert results == ["a", "b", "c"]


    async def test_anext_builtin():
        \"\"\"Test using anext() builtin (Python 3.10+).\"\"\"
        gen = number_stream(5)

        first = await anext(gen)
        second = await anext(gen)

        assert first == 0
        assert second == 1

        # Can use default value
        # last = await anext(exhausted_gen, default=-1)
    """)

    # Demo
    print("6. Running Async Generators (Demo)")
    print("-" * 40)

    async def demo() -> None:
        print("Number stream (5 items):")
        async for num in number_stream(5):
            print(f"  {num}")

        print("\nPaginated fetch (10 items, page_size=3):")
        async for page in paginated_fetch(10, 3):
            print(f"  Page: {[item['id'] for item in page]}")

        print("\nEvent stream with early break:")
        async for event in event_stream(10):
            print(f"  Event: {event['event_id']}")
            if event["event_id"] >= 2:
                print("  Breaking early...")
                break

        print("\nAsync iterable collection:")
        collection = AsyncIterableCollection(["first", "second", "third"])
        async for item in collection:
            print(f"  Item: {item}")

    asyncio.run(demo())

    print()
    print("Run the tests with:")
    print("  pytest tests/test_async_generators.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

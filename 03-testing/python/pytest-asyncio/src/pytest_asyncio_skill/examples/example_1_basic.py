"""Example 1: Basic Async Testing

This example demonstrates the fundamentals of testing async functions
with pytest-asyncio, including basic tests and the auto mode.
"""

import asyncio


async def fetch_data(key: str) -> dict[str, str]:
    """Simulate fetching data asynchronously."""
    await asyncio.sleep(0.01)  # Simulate network delay
    return {"key": key, "value": f"data_for_{key}"}


async def calculate_async(a: int, b: int) -> int:
    """Simulate an async calculation."""
    await asyncio.sleep(0.01)  # Simulate processing
    return a + b


async def process_items(items: list[str]) -> list[str]:
    """Process items asynchronously."""
    results = []
    for item in items:
        await asyncio.sleep(0.01)  # Simulate processing each item
        results.append(item.upper())
    return results


def main() -> None:
    """Demonstrate basic async testing concepts."""
    print("Example 1: Basic Async Testing")
    print("=" * 50)
    print()

    # Show basic async test pattern
    print("1. Basic Async Test")
    print("-" * 40)
    print("""
    import pytest

    # With explicit marker
    @pytest.mark.asyncio
    async def test_fetch_data():
        result = await fetch_data("user_1")
        assert result["key"] == "user_1"
        assert result["value"] == "data_for_user_1"

    # With auto mode (asyncio_mode = "auto" in pyproject.toml)
    # No marker needed - pytest-asyncio detects async functions
    async def test_fetch_data_auto():
        result = await fetch_data("user_1")
        assert result["key"] == "user_1"
    """)

    # Show what happens without proper setup
    print("2. Common Mistake: Missing Await")
    print("-" * 40)
    print("""
    async def test_forgot_await():
        # WRONG - result is a coroutine, not the actual value!
        result = fetch_data("user_1")  # Missing await
        print(type(result))  # <class 'coroutine'>
        # assert result["key"] == "user_1"  # TypeError!

        # RIGHT - await the coroutine
        result = await fetch_data("user_1")
        assert result["key"] == "user_1"
    """)

    # Show testing exceptions
    print("3. Testing Async Exceptions")
    print("-" * 40)
    print("""
    import pytest

    async def risky_operation(fail: bool = False):
        await asyncio.sleep(0.01)
        if fail:
            raise ValueError("Operation failed!")
        return "success"

    async def test_async_exception():
        # Test that exception is raised
        with pytest.raises(ValueError, match="Operation failed"):
            await risky_operation(fail=True)

        # Test successful operation
        result = await risky_operation(fail=False)
        assert result == "success"
    """)

    # Show testing return values
    print("4. Testing Async Return Values")
    print("-" * 40)
    print("""
    async def test_calculate_async():
        result = await calculate_async(2, 3)
        assert result == 5

    async def test_process_items():
        items = ["hello", "world"]
        result = await process_items(items)
        assert result == ["HELLO", "WORLD"]
        assert len(result) == len(items)
    """)

    # Demonstrate running async code
    print("5. Running Async Code (Demo)")
    print("-" * 40)

    async def demo() -> None:
        # Fetch data
        data = await fetch_data("demo_key")
        print(f"Fetched data: {data}")

        # Calculate
        sum_result = await calculate_async(10, 20)
        print(f"Calculation result: {sum_result}")

        # Process items
        processed = await process_items(["test", "demo"])
        print(f"Processed items: {processed}")

    asyncio.run(demo())

    print()
    print("Run the tests with:")
    print("  pytest tests/test_basic_async.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

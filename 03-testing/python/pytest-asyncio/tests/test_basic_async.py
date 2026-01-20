"""Tests demonstrating basic async testing with pytest-asyncio.

With asyncio_mode = "auto" in pyproject.toml, async test functions
are automatically detected and run with pytest-asyncio.
"""

import asyncio

import pytest


# =============================================================================
# Basic Async Functions to Test
# =============================================================================


async def fetch_data(key: str) -> dict[str, str]:
    """Simulate fetching data asynchronously."""
    await asyncio.sleep(0.01)
    return {"key": key, "value": f"data_for_{key}"}


async def calculate_async(a: int, b: int) -> int:
    """Simulate an async calculation."""
    await asyncio.sleep(0.01)
    return a + b


async def risky_operation(fail: bool = False) -> str:
    """Operation that may fail."""
    await asyncio.sleep(0.01)
    if fail:
        raise ValueError("Operation failed!")
    return "success"


# =============================================================================
# Basic Async Tests
# =============================================================================


async def test_fetch_data() -> None:
    """Test basic async function call."""
    result = await fetch_data("user_1")

    assert result["key"] == "user_1"
    assert result["value"] == "data_for_user_1"


async def test_calculate_async() -> None:
    """Test async calculation."""
    result = await calculate_async(2, 3)
    assert result == 5


async def test_multiple_async_calls() -> None:
    """Test multiple sequential async calls."""
    data1 = await fetch_data("key1")
    data2 = await fetch_data("key2")

    assert data1["key"] == "key1"
    assert data2["key"] == "key2"


# =============================================================================
# Testing Exceptions
# =============================================================================


async def test_async_exception_raised() -> None:
    """Test that async function raises expected exception."""
    with pytest.raises(ValueError, match="Operation failed"):
        await risky_operation(fail=True)


async def test_async_success_and_failure() -> None:
    """Test both success and failure paths."""
    # Success path
    result = await risky_operation(fail=False)
    assert result == "success"

    # Failure path
    with pytest.raises(ValueError):
        await risky_operation(fail=True)


async def test_exception_message() -> None:
    """Test exception message content."""
    try:
        await risky_operation(fail=True)
        pytest.fail("Expected ValueError to be raised")
    except ValueError as e:
        assert "Operation failed" in str(e)


# =============================================================================
# Testing Return Values
# =============================================================================


async def test_return_type() -> None:
    """Test return value type."""
    result = await fetch_data("test")
    assert isinstance(result, dict)
    assert "key" in result
    assert "value" in result


async def test_return_value_equality() -> None:
    """Test return value equality."""
    result1 = await fetch_data("same_key")
    result2 = await fetch_data("same_key")

    # Results should be equal (same input, same output)
    assert result1 == result2


async def test_calculation_edge_cases() -> None:
    """Test calculation with various inputs."""
    assert await calculate_async(0, 0) == 0
    assert await calculate_async(-1, 1) == 0
    assert await calculate_async(100, 200) == 300
    assert await calculate_async(-50, -50) == -100


# =============================================================================
# Testing with Assertions
# =============================================================================


async def test_multiple_assertions() -> None:
    """Test with multiple assertions."""
    result = await fetch_data("multi_test")

    # Multiple assertions on the result
    assert result is not None
    assert len(result) == 2
    assert result["key"] == "multi_test"
    assert result["value"].startswith("data_for_")
    assert result["value"].endswith("multi_test")


async def test_async_function_called() -> None:
    """Verify async function actually executes."""
    call_count = 0

    async def tracked_function() -> str:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        return "done"

    result = await tracked_function()

    assert result == "done"
    assert call_count == 1


# =============================================================================
# Explicit Marker (Alternative to auto mode)
# =============================================================================


@pytest.mark.asyncio
async def test_with_explicit_marker() -> None:
    """Test with explicit @pytest.mark.asyncio marker.

    When using asyncio_mode = "auto", this marker is optional
    but can still be used for clarity or compatibility.
    """
    result = await calculate_async(5, 5)
    assert result == 10


# =============================================================================
# Test Class with Async Methods
# =============================================================================


class TestAsyncClass:
    """Test class containing async test methods."""

    async def test_class_method(self) -> None:
        """Async test method in a class."""
        result = await fetch_data("class_test")
        assert result["key"] == "class_test"

    async def test_another_class_method(self) -> None:
        """Another async test method."""
        result = await calculate_async(10, 20)
        assert result == 30

    async def test_with_instance_state(self) -> None:
        """Test that can use instance attributes."""
        self.test_data = await fetch_data("instance_test")
        assert self.test_data is not None

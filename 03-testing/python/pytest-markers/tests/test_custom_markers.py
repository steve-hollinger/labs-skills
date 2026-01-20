"""Tests demonstrating custom pytest markers.

This module shows how to define and use custom markers for
test categorization and selective execution.
"""

import time

import pytest


# =============================================================================
# Speed-based Markers
# =============================================================================


@pytest.mark.fast
def test_fast_operation() -> None:
    """A fast test that completes quickly."""
    result = 2 + 2
    assert result == 4


@pytest.mark.fast
def test_another_fast_operation() -> None:
    """Another quick test."""
    data = [1, 2, 3]
    assert len(data) == 3


@pytest.mark.slow
def test_slow_operation() -> None:
    """A slow test (simulated with sleep)."""
    time.sleep(0.1)  # Simulate slow operation
    assert True


@pytest.mark.slow
def test_complex_calculation() -> None:
    """Test involving complex computation."""
    # Simulate heavy computation
    result = sum(i * i for i in range(1000))
    assert result == 332833500


# =============================================================================
# Test Type Markers
# =============================================================================


@pytest.mark.unit
def test_pure_function() -> None:
    """Unit test for a pure function with no side effects."""

    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


@pytest.mark.unit
def test_string_processing() -> None:
    """Unit test for string manipulation."""

    def normalize_name(name: str) -> str:
        return name.strip().title()

    assert normalize_name("  john doe  ") == "John Doe"
    assert normalize_name("JANE") == "Jane"


@pytest.mark.integration
def test_file_operations(tmp_path: pytest.TempPathFactory) -> None:
    """Integration test involving file system."""
    # tmp_path is a pytest fixture providing a temporary directory
    test_file = tmp_path / "test.txt"  # type: ignore[operator]
    test_file.write_text("Hello, World!")

    content = test_file.read_text()
    assert content == "Hello, World!"


@pytest.mark.integration
@pytest.mark.database
def test_simulated_database() -> None:
    """Integration test simulating database operations."""

    # Simulated in-memory database
    class FakeDB:
        def __init__(self) -> None:
            self._data: dict[str, dict[str, str]] = {}

        def save(self, table: str, data: dict[str, str]) -> None:
            self._data[table] = data

        def get(self, table: str) -> dict[str, str] | None:
            return self._data.get(table)

    db = FakeDB()
    db.save("users", {"name": "Test User"})
    result = db.get("users")

    assert result == {"name": "Test User"}


# =============================================================================
# Feature Markers
# =============================================================================


@pytest.mark.api
def test_api_validation() -> None:
    """Test API input validation logic."""

    def validate_request(data: dict[str, str]) -> bool:
        return "id" in data and "name" in data

    assert validate_request({"id": "1", "name": "Test"})
    assert not validate_request({"id": "1"})
    assert not validate_request({})


@pytest.mark.smoke
def test_application_health() -> None:
    """Smoke test to verify basic application health."""

    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": "1.0.0"}

    result = health_check()
    assert result["status"] == "healthy"


@pytest.mark.regression
def test_bug_fix_123() -> None:
    """Regression test for Bug #123: off-by-one error."""

    def get_items(data: list[int], count: int) -> list[int]:
        # Fixed: was using count instead of count correctly
        return data[:count]

    assert get_items([1, 2, 3, 4, 5], 3) == [1, 2, 3]
    assert get_items([1, 2, 3], 5) == [1, 2, 3]  # Bug was here


# =============================================================================
# Multiple Markers
# =============================================================================


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.database
def test_full_sync() -> None:
    """Test with multiple markers - slow, integration, and database."""
    time.sleep(0.1)  # Simulate slow database sync
    assert True


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.smoke
def test_critical_path() -> None:
    """Critical path test - fast, unit, and smoke markers."""

    def is_valid(value: int) -> bool:
        return value > 0

    assert is_valid(1)


# =============================================================================
# Class-level Markers
# =============================================================================


@pytest.mark.database
class TestDatabaseOperations:
    """All tests in this class are marked as database tests."""

    def test_insert(self) -> None:
        """Inherits @database marker from class."""
        assert True

    def test_update(self) -> None:
        """Inherits @database marker from class."""
        assert True

    def test_delete(self) -> None:
        """Inherits @database marker from class."""
        assert True

    @pytest.mark.slow
    def test_bulk_operation(self) -> None:
        """Has both @database (from class) and @slow markers."""
        time.sleep(0.1)
        assert True


@pytest.mark.unit
@pytest.mark.fast
class TestMathOperations:
    """Fast unit tests for math operations."""

    def test_add(self) -> None:
        """Test addition."""
        assert 1 + 1 == 2

    def test_subtract(self) -> None:
        """Test subtraction."""
        assert 5 - 3 == 2

    def test_multiply(self) -> None:
        """Test multiplication."""
        assert 3 * 4 == 12

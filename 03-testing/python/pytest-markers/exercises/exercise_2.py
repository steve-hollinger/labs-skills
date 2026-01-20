"""Exercise 2: Create Custom Markers for a Testing Workflow

Your task is to create a test suite with custom markers for a CI/CD pipeline.
The pipeline has these stages:
1. Smoke tests (quick sanity checks, < 1 second each)
2. Unit tests (isolated, no I/O)
3. Integration tests (require database or network)
4. End-to-end tests (full workflow, slow)

Instructions:
1. Add custom markers to each test function
2. Tests can have multiple markers if appropriate
3. Create a class with a class-level marker
4. Add a module-level marker for all tests in one section

Expected Results:
When running with marker filters:
- `pytest -m smoke` should run 2 tests
- `pytest -m unit` should run 3 tests
- `pytest -m integration` should run 2 tests
- `pytest -m e2e` should run 1 test
- `pytest -m "not slow"` should skip slow tests

Hints:
- Use @pytest.mark.<marker_name> syntax
- Class-level markers apply to all methods
- Module-level markers use pytestmark = pytest.mark.<name>

Run your tests with:
    pytest exercises/exercise_2.py -v -m smoke
    pytest exercises/exercise_2.py -v -m "not slow"
"""

import pytest  # noqa: F401

# TODO: Add module-level marker if needed
# pytestmark = pytest.mark.???


# =============================================================================
# Smoke Tests - Quick sanity checks
# =============================================================================

# TODO: Add appropriate marker(s)
def test_app_starts() -> None:
    """Verify application can start."""
    app = {"status": "running"}
    assert app["status"] == "running"


# TODO: Add appropriate marker(s)
def test_config_loads() -> None:
    """Verify configuration loads correctly."""
    config = {"db_url": "postgres://localhost/test"}
    assert "db_url" in config


# =============================================================================
# Unit Tests - Fast, isolated
# =============================================================================

# TODO: Add appropriate marker(s)
def test_calculate_discount() -> None:
    """Test discount calculation logic."""

    def calculate_discount(price: float, percent: float) -> float:
        return price * (1 - percent / 100)

    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 50) == 25


# TODO: Add appropriate marker(s)
def test_validate_email() -> None:
    """Test email validation."""

    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    assert is_valid_email("test@example.com")
    assert not is_valid_email("invalid")


# TODO: Add appropriate marker(s)
def test_format_currency() -> None:
    """Test currency formatting."""

    def format_currency(amount: float) -> str:
        return f"${amount:.2f}"

    assert format_currency(10) == "$10.00"
    assert format_currency(99.999) == "$100.00"


# =============================================================================
# Integration Tests - Require external resources
# =============================================================================

# TODO: Add appropriate marker(s) - this is an integration test with database
def test_database_connection() -> None:
    """Test database connection."""
    # Simulated database connection
    db = {"connected": True}
    assert db["connected"]


# TODO: Add appropriate marker(s) - this is slow and requires API
def test_api_authentication() -> None:
    """Test API authentication flow."""
    import time

    time.sleep(0.1)  # Simulate API call
    token = {"valid": True, "expires": 3600}
    assert token["valid"]


# =============================================================================
# End-to-End Tests - Full workflow, always slow
# =============================================================================

# TODO: Add a class-level marker for e2e and slow
class TestCheckoutWorkflow:
    """End-to-end checkout workflow tests."""

    def test_add_to_cart(self) -> None:
        """Add item to cart."""
        cart = []
        cart.append({"id": 1, "name": "Widget"})
        assert len(cart) == 1

    def test_apply_coupon(self) -> None:
        """Apply discount coupon."""
        total = 100
        discount = 10
        assert total - discount == 90

    def test_complete_purchase(self) -> None:
        """Complete the purchase."""
        order = {"status": "completed", "id": 12345}
        assert order["status"] == "completed"


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v", "--collect-only"])

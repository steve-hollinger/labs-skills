"""Solution for Exercise 2: Create Custom Markers for a Testing Workflow

This solution demonstrates organizing tests with custom markers for CI/CD.
"""

import time

import pytest


# =============================================================================
# Smoke Tests - Quick sanity checks
# =============================================================================


@pytest.mark.smoke
@pytest.mark.fast
def test_app_starts() -> None:
    """Verify application can start."""
    app = {"status": "running"}
    assert app["status"] == "running"


@pytest.mark.smoke
@pytest.mark.fast
def test_config_loads() -> None:
    """Verify configuration loads correctly."""
    config = {"db_url": "postgres://localhost/test"}
    assert "db_url" in config


# =============================================================================
# Unit Tests - Fast, isolated
# =============================================================================


@pytest.mark.unit
@pytest.mark.fast
def test_calculate_discount() -> None:
    """Test discount calculation logic."""

    def calculate_discount(price: float, percent: float) -> float:
        return price * (1 - percent / 100)

    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 50) == 25


@pytest.mark.unit
@pytest.mark.fast
def test_validate_email() -> None:
    """Test email validation."""

    def is_valid_email(email: str) -> bool:
        return "@" in email and "." in email.split("@")[-1]

    assert is_valid_email("test@example.com")
    assert not is_valid_email("invalid")


@pytest.mark.unit
@pytest.mark.fast
def test_format_currency() -> None:
    """Test currency formatting."""

    def format_currency(amount: float) -> str:
        return f"${amount:.2f}"

    assert format_currency(10) == "$10.00"
    assert format_currency(99.999) == "$100.00"


# =============================================================================
# Integration Tests - Require external resources
# =============================================================================


@pytest.mark.integration
@pytest.mark.database
def test_database_connection() -> None:
    """Test database connection."""
    # Simulated database connection
    db = {"connected": True}
    assert db["connected"]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
def test_api_authentication() -> None:
    """Test API authentication flow."""
    time.sleep(0.1)  # Simulate API call
    token = {"valid": True, "expires": 3600}
    assert token["valid"]


# =============================================================================
# End-to-End Tests - Full workflow, always slow
# =============================================================================


@pytest.mark.e2e
@pytest.mark.slow
class TestCheckoutWorkflow:
    """End-to-end checkout workflow tests."""

    def test_add_to_cart(self) -> None:
        """Add item to cart."""
        cart: list[dict[str, int | str]] = []
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

    print("Running smoke tests:")
    subprocess.run(["pytest", __file__, "-v", "-m", "smoke"])

    print("\nRunning unit tests:")
    subprocess.run(["pytest", __file__, "-v", "-m", "unit"])

    print("\nRunning non-slow tests:")
    subprocess.run(["pytest", __file__, "-v", "-m", "not slow"])

"""Pytest configuration for pytest-markers skill tests.

This conftest.py demonstrates marker-related fixtures and hooks.
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers dynamically."""
    # These are in addition to markers defined in pyproject.toml
    config.addinivalue_line(
        "markers", "requires_env(name): skip if environment variable not set"
    )
    config.addinivalue_line(
        "markers", "min_python(major, minor): skip if Python version is lower"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection based on markers.

    This hook runs after all tests are collected and allows us to:
    - Add markers to tests
    - Skip tests based on conditions
    - Reorder tests
    """
    for item in items:
        # Add 'fast' marker to any test not marked as 'slow'
        if not item.get_closest_marker("slow"):
            # Only add if it doesn't already have 'fast'
            if not item.get_closest_marker("fast"):
                pass  # Don't auto-add markers in this example

        # Handle requires_env marker
        for marker in item.iter_markers(name="requires_env"):
            import os

            env_name = marker.args[0]
            if not os.environ.get(env_name):
                item.add_marker(
                    pytest.mark.skip(reason=f"Environment variable {env_name} not set")
                )


@pytest.fixture
def slow_resource() -> str:
    """Fixture that simulates a slow resource setup."""
    import time

    time.sleep(0.05)  # Simulate slow setup
    return "slow_resource_data"


@pytest.fixture
def marker_info(request: pytest.FixtureRequest) -> dict[str, list[str]]:
    """Fixture that provides information about markers on the current test."""
    markers = list(request.node.iter_markers())
    return {
        "marker_names": [m.name for m in markers],
        "marker_count": len(markers),
    }

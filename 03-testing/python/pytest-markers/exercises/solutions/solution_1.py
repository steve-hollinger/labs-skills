"""Solution for Exercise 1: Organize Tests with Built-in Markers

This solution demonstrates proper usage of skip, skipif, and xfail markers.
"""

import sys

import pytest


@pytest.mark.skip(reason="Feature planned for v2.0, not yet implemented")
def test_unimplemented_feature() -> None:
    """This feature is planned for v2.0 but not yet implemented."""
    from future_module import new_feature  # type: ignore  # noqa: F401

    assert new_feature() == "result"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_windows_only() -> None:
    """This test requires Windows-specific APIs."""
    import ctypes  # noqa: F401

    # Windows-specific code
    assert True


@pytest.mark.skipif(
    sys.version_info < (3, 12), reason="Requires Python 3.12+ features"
)
def test_python_312_feature() -> None:
    """This test uses Python 3.12+ syntax features."""
    # Simulated 3.12+ feature
    assert True


@pytest.mark.xfail(reason="Bug #456: Division truncates instead of rounding")
def test_known_bug() -> None:
    """Bug #456: Division truncates instead of rounding."""

    def broken_divide(a: int, b: int) -> int:
        return a // b  # Bug: should use round(a/b)

    assert broken_divide(5, 2) == 3  # Should be 3, but returns 2


@pytest.mark.xfail(reason="Flaky network test - timing dependent", strict=False)
def test_flaky_network() -> None:
    """This test occasionally fails due to network timing."""
    import random

    # Simulate flaky behavior
    if random.random() < 0.5:
        raise TimeoutError("Network timeout")
    assert True


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

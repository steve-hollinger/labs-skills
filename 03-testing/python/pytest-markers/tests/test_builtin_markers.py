"""Tests demonstrating built-in pytest markers.

This module shows how to use skip, skipif, and xfail markers
in practical test scenarios.
"""

import platform
import sys

import pytest


# =============================================================================
# Skip Marker Tests
# =============================================================================


@pytest.mark.skip(reason="Demonstrating unconditional skip")
def test_skip_always() -> None:
    """This test is always skipped."""
    assert False, "Should never reach this"


@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature() -> None:
    """Placeholder for future functionality."""
    # This is a common pattern for TDD - write the test first
    from pytest_markers import future_module  # type: ignore  # noqa: F401

    assert future_module.new_function() == "expected"


# =============================================================================
# Skipif Marker Tests
# =============================================================================


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+")
def test_python_311_feature() -> None:
    """Test that requires Python 3.11 or newer."""
    # Example: match statement was finalized in 3.10, but we test 3.11+ features
    assert sys.version_info >= (3, 11)


@pytest.mark.skipif(sys.version_info >= (3, 12), reason="Deprecated in Python 3.12+")
def test_deprecated_feature() -> None:
    """Test for feature deprecated in newer Python."""
    # Could test something that changed behavior
    assert True


@pytest.mark.skipif(platform.system() == "Windows", reason="Unix-only feature")
def test_unix_specific() -> None:
    """Test that only runs on Unix-like systems."""
    # On Unix, these imports work
    if platform.system() != "Windows":
        import pwd  # noqa: F401

        assert True
    else:
        pytest.fail("Should not run on Windows")


@pytest.mark.skipif(
    platform.system() != "Darwin", reason="macOS-only test"
)
def test_macos_specific() -> None:
    """Test that only runs on macOS."""
    assert platform.system() == "Darwin"


# Multiple skipif conditions (OR logic - skips if ANY condition is True)
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Needs Python 3.10+")
@pytest.mark.skipif(platform.system() == "Windows", reason="Not on Windows")
def test_multiple_skip_conditions() -> None:
    """Test with multiple skip conditions."""
    # Skipped if Python < 3.10 OR if on Windows
    assert sys.version_info >= (3, 10)
    assert platform.system() != "Windows"


# =============================================================================
# Xfail Marker Tests
# =============================================================================


@pytest.mark.xfail(reason="Demonstrating expected failure")
def test_xfail_basic() -> None:
    """Test expected to fail - demonstrates xfail behavior."""
    # This assertion will fail, but the test is marked as xfail
    # so the overall test result is "xfailed" (expected)
    assert 1 == 2, "This failure is expected"


@pytest.mark.xfail(reason="Known bug #123: incorrect rounding")
def test_known_bug() -> None:
    """Test documenting a known bug."""

    def buggy_round(value: float) -> int:
        # Bug: should use round(), uses int() instead
        return int(value)

    # This test documents the bug while it's being fixed
    result = buggy_round(2.7)
    assert result == 3  # Fails because int(2.7) == 2


@pytest.mark.xfail(reason="This passes, showing XPASS", strict=False)
def test_xfail_but_passes() -> None:
    """Test marked xfail that actually passes (XPASS)."""
    # When strict=False (default), passing is OK (shows as XPASS)
    assert 1 == 1


@pytest.mark.xfail(reason="Should fail", strict=True)
def test_xfail_strict() -> None:
    """Strict xfail - test MUST fail, or it's an error."""
    # With strict=True, if this test passes, it's a FAILURE
    # This is useful for ensuring known bugs stay "broken"
    # until you explicitly fix them
    assert False, "This must fail for the test to pass"


@pytest.mark.xfail(
    sys.version_info >= (3, 11),
    reason="Behavior changed in Python 3.11",
)
def test_xfail_conditional() -> None:
    """Conditional xfail based on Python version."""
    # Only expected to fail on Python 3.11+
    # This is useful when a library has version-specific issues
    if sys.version_info >= (3, 11):
        assert False, "Expected to fail on 3.11+"
    else:
        assert True


@pytest.mark.xfail(raises=ZeroDivisionError, reason="Division by zero expected")
def test_xfail_specific_exception() -> None:
    """Test expected to raise a specific exception."""
    # Only counts as xfail if ZeroDivisionError is raised
    _ = 1 / 0


# =============================================================================
# Combined Marker Tests
# =============================================================================


class TestBuiltinMarkerCombinations:
    """Test class demonstrating marker combinations."""

    @pytest.mark.skipif(
        sys.version_info < (3, 11) and platform.system() == "Windows",
        reason="Combination: old Python on Windows",
    )
    def test_combined_condition(self) -> None:
        """Skip only if BOTH conditions are true."""
        assert True

    @pytest.mark.xfail(reason="Known issue")
    @pytest.mark.skipif(platform.system() == "Windows", reason="Not on Windows")
    def test_xfail_and_skipif(self) -> None:
        """Combining xfail and skipif markers."""
        # On Windows: skipped
        # On Unix: expected to fail
        assert False

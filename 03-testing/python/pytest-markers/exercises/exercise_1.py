"""Exercise 1: Organize Tests with Built-in Markers

Your task is to add appropriate markers to the tests below.
Each test has a comment describing its characteristics.

Instructions:
1. Add @pytest.mark.skip or @pytest.mark.skipif where appropriate
2. Add @pytest.mark.xfail for tests with known issues
3. Do NOT modify the test logic, only add markers

Expected Behavior:
- test_unimplemented_feature: Should be skipped (not implemented)
- test_windows_only: Should only run on Windows
- test_python_312_feature: Should only run on Python 3.12+
- test_known_bug: Should be expected to fail
- test_flaky_network: Should be expected to fail (strict=False)

Hints:
- Use sys.platform to check operating system
- Use sys.version_info to check Python version
- Remember to import pytest at the top

Run your tests with:
    pytest exercises/exercise_1.py -v
"""

# TODO: Add necessary imports here


def test_unimplemented_feature() -> None:
    """This feature is planned for v2.0 but not yet implemented.

    Add a marker to skip this test with an appropriate reason.
    """
    from future_module import new_feature  # type: ignore  # noqa: F401

    assert new_feature() == "result"


def test_windows_only() -> None:
    """This test requires Windows-specific APIs.

    Add a marker to skip on non-Windows platforms.
    """
    import ctypes  # noqa: F401

    # Windows-specific code
    assert True


def test_python_312_feature() -> None:
    """This test uses Python 3.12+ syntax features.

    Add a marker to skip on Python versions below 3.12.
    """
    # Simulated 3.12+ feature
    assert True


def test_known_bug() -> None:
    """Bug #456: Division truncates instead of rounding.

    Add a marker to mark this as an expected failure.
    The function should round but currently truncates.
    """

    def broken_divide(a: int, b: int) -> int:
        return a // b  # Bug: should use round(a/b)

    assert broken_divide(5, 2) == 3  # Should be 3, but returns 2


def test_flaky_network() -> None:
    """This test occasionally fails due to network timing.

    Add a marker for expected failure that's NOT strict
    (so passing is OK too).
    """
    import random

    # Simulate flaky behavior
    if random.random() < 0.5:
        raise TimeoutError("Network timeout")
    assert True


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

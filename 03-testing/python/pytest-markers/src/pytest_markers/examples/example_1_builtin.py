"""Example 1: Built-in Markers

This example demonstrates pytest's built-in markers:
- @pytest.mark.skip - Skip a test unconditionally
- @pytest.mark.skipif - Skip a test based on a condition
- @pytest.mark.xfail - Mark a test as expected to fail
"""

import platform
import sys


def main() -> None:
    """Demonstrate built-in pytest markers."""
    print("Example 1: Built-in Markers")
    print("=" * 50)
    print()

    # Show skip marker usage
    print("1. @pytest.mark.skip - Unconditional Skip")
    print("-" * 40)
    print("""
    @pytest.mark.skip(reason="Feature not implemented yet")
    def test_future_feature():
        # This test will never run
        assert some_future_function() == expected

    Use cases:
    - Tests for features not yet implemented
    - Temporarily disabling flaky tests
    - Placeholder tests in TDD
    """)

    # Show skipif marker usage
    print("2. @pytest.mark.skipif - Conditional Skip")
    print("-" * 40)
    print(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"Current platform: {platform.system()}")
    print("""
    @pytest.mark.skipif(
        sys.version_info < (3, 11),
        reason="Requires Python 3.11+ for match statement"
    )
    def test_match_statement():
        match value:
            case 1: result = "one"
            case _: result = "other"

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Unix-only feature"
    )
    def test_unix_permissions():
        import pwd  # Unix-only module
        assert pwd.getpwuid(0).pw_name == "root"
    """)

    # Show xfail marker usage
    print("3. @pytest.mark.xfail - Expected Failure")
    print("-" * 40)
    print("""
    @pytest.mark.xfail(reason="Bug #123: Division by zero not handled")
    def test_known_bug():
        result = divide(1, 0)  # Will raise, but test 'passes'
        assert result == float('inf')

    With strict=True, test FAILS if it unexpectedly passes:

    @pytest.mark.xfail(reason="Should fail", strict=True)
    def test_strict_xfail():
        assert False  # Expected - test passes
        # If this asserted True, test would FAIL

    Use cases:
    - Documenting known bugs
    - Tests for unimplemented features
    - Platform-specific known issues
    """)

    # Show combining markers
    print("4. Combining Skip Markers")
    print("-" * 40)
    print("""
    # Skip on Windows AND old Python
    @pytest.mark.skipif(
        sys.platform == "win32" and sys.version_info < (3, 10),
        reason="Windows + Python < 3.10 has issues"
    )
    def test_windows_new_python():
        pass

    # Multiple skipif markers (OR logic)
    @pytest.mark.skipif(sys.platform == "win32", reason="No Windows")
    @pytest.mark.skipif(sys.platform == "darwin", reason="No macOS")
    def test_linux_only():
        # Skips on Windows OR macOS
        pass
    """)

    print()
    print("Run the tests to see markers in action:")
    print("  pytest tests/test_builtin_markers.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

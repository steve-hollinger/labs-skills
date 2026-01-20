"""Exercise 3: Implement a Generic Data Structure

Goal: Create a fully-typed generic Result type for error handling.

Instructions:
1. Implement the Result[T] generic class
2. Add Ok and Err factory functions
3. Implement all methods with proper types
4. Make sure the code passes `mypy --strict`

The Result type should:
- Hold either a success value of type T or an error message
- Provide methods to check success/failure
- Provide methods to unwrap values safely
- Support mapping operations

Example Usage:
    result: Result[int] = Ok(42)
    if result.is_ok():
        value = result.unwrap()
        print(f"Got: {value}")

    result: Result[int] = Err("something went wrong")
    if result.is_err():
        print(f"Error: {result.error()}")

Hints:
- Use TypeVar for the generic type T
- Use @overload if needed for different return types
- The map() method should return Result[U] where U is the new type
"""

from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Result(Generic[T]):
    """A generic Result type for error handling.

    Represents either a successful value (Ok) or an error (Err).
    Similar to Rust's Result type.
    """

    def __init__(self, value: T | None = None, error: str | None = None) -> None:
        """Initialize Result with either a value or an error.

        TODO: Implement this method.
        - Store the value and error
        - Ensure exactly one of value/error is set (for Err, value should be None)
        """
        pass

    def is_ok(self) -> bool:
        """Return True if this is a successful result.

        TODO: Implement this method.
        """
        pass

    def is_err(self) -> bool:
        """Return True if this is an error result.

        TODO: Implement this method.
        """
        pass

    def unwrap(self) -> T:
        """Return the value if Ok, raise ValueError if Err.

        TODO: Implement this method.
        - If this is Ok, return the value
        - If this is Err, raise ValueError with the error message
        """
        pass

    def unwrap_or(self, default: T) -> T:
        """Return the value if Ok, or the default if Err.

        TODO: Implement this method.
        """
        pass

    def error(self) -> str | None:
        """Return the error message if Err, None if Ok.

        TODO: Implement this method.
        """
        pass

    def map(self, func: Callable[[T], U]) -> "Result[U]":
        """Apply a function to the value if Ok, pass through Err.

        TODO: Implement this method.
        - If Ok, return Result with func(value)
        - If Err, return Result with same error
        """
        pass


def Ok(value: T) -> Result[T]:
    """Create a successful Result.

    TODO: Implement this factory function.
    """
    pass


def Err(error: str) -> Result[T]:
    """Create an error Result.

    TODO: Implement this factory function.
    Note: This should work for any type T.
    """
    pass


# ============================================
# TEST CASES
# ============================================

def test_result() -> None:
    """Test the Result implementation."""
    print("Testing Result implementation...")

    # Test Ok
    ok_result: Result[int] = Ok(42)
    assert ok_result.is_ok(), "Ok should be ok"
    assert not ok_result.is_err(), "Ok should not be err"
    assert ok_result.unwrap() == 42, "unwrap should return value"
    assert ok_result.unwrap_or(0) == 42, "unwrap_or should return value"
    assert ok_result.error() is None, "error should be None for Ok"
    print("  Ok tests passed")

    # Test Err
    err_result: Result[int] = Err("something went wrong")
    assert not err_result.is_ok(), "Err should not be ok"
    assert err_result.is_err(), "Err should be err"
    assert err_result.unwrap_or(0) == 0, "unwrap_or should return default"
    assert err_result.error() == "something went wrong", "error should return message"
    print("  Err tests passed")

    # Test unwrap raises on Err
    try:
        err_result.unwrap()
        assert False, "unwrap on Err should raise"
    except ValueError as e:
        assert "something went wrong" in str(e)
        print("  unwrap raise test passed")

    # Test map
    ok_result2: Result[int] = Ok(5)
    mapped: Result[str] = ok_result2.map(lambda x: str(x * 2))
    assert mapped.is_ok(), "mapped Ok should be ok"
    assert mapped.unwrap() == "10", "mapped value should be '10'"
    print("  map on Ok test passed")

    err_result2: Result[int] = Err("error")
    mapped_err: Result[str] = err_result2.map(lambda x: str(x))
    assert mapped_err.is_err(), "mapped Err should be err"
    assert mapped_err.error() == "error", "mapped error should preserve message"
    print("  map on Err test passed")

    print("\nAll tests passed!")


def verify_types() -> None:
    """Run mypy to verify types."""
    import subprocess

    result = subprocess.run(
        ["mypy", "--strict", __file__],
        capture_output=True,
        text=True,
    )

    print("\nMyPy Output:")
    print("-" * 40)
    if result.stdout:
        print(result.stdout)
    print("-" * 40)

    if result.returncode == 0:
        print("Type check passed!")
    else:
        print("Type errors remain.")


if __name__ == "__main__":
    print(__doc__)

    # Uncomment to run tests after implementing
    # test_result()
    # verify_types()

    print("\nImplement the Result class, then run:")
    print("  python exercises/exercise_3.py")

"""Exercise 3: Parametrized Test Matrix

Your task is to create parametrized tests for a password validation function.

The password validator should check:
- Minimum length (8 characters)
- Contains uppercase letter
- Contains lowercase letter
- Contains digit
- Contains special character (!@#$%^&*)

Instructions:
1. Complete the `validate_password` function
2. Create parametrized tests covering all validation rules
3. Use meaningful test IDs
4. Use pytest.param for special cases with marks
5. Create a test matrix for edge cases

Expected Test Cases:
- Valid passwords (should pass all checks)
- Too short (< 8 chars)
- Missing uppercase
- Missing lowercase
- Missing digit
- Missing special char
- Empty string
- Only spaces

Hints:
- Use @pytest.mark.parametrize with "password,is_valid,reason"
- Use ids= parameter for readable test names
- Use pytest.param() for cases that need marks

Run your tests with:
    pytest exercises/exercise_3.py -v
"""

import pytest  # noqa: F401


def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password against security requirements.

    Returns:
        tuple: (is_valid, error_message or "OK")

    TODO: Implement this function to check:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character from: !@#$%^&*
    """
    # TODO: Implement password validation
    # Return (True, "OK") if valid
    # Return (False, "reason") if invalid
    pass


# TODO: Add parametrized test for valid passwords
# Test at least 3 different valid passwords
def test_valid_passwords() -> None:
    """Test passwords that should be valid."""
    # TODO: Convert to parametrized test
    pass


# TODO: Add parametrized test for invalid passwords
# Each test case should have: password, expected_valid, expected_reason
# Use meaningful IDs like "too_short", "no_uppercase", etc.
def test_invalid_passwords() -> None:
    """Test passwords that should be invalid."""
    # TODO: Convert to parametrized test with multiple cases
    pass


# TODO: Create a test matrix for edge cases
# Parametrize with: special characters, lengths, case variations
def test_edge_cases() -> None:
    """Test edge cases in password validation."""
    # TODO: Implement parametrized edge case tests
    pass


# TODO: Add a parametrized test using pytest.param with marks
# Include an xfail case for a known limitation
def test_special_cases() -> None:
    """Test special cases with appropriate marks."""
    # TODO: Use pytest.param for cases like:
    # - Very long password (mark as slow if > 1000 chars)
    # - Unicode characters (mark as xfail if not supported)
    pass


# Bonus: Create a test class with parametrized methods
class TestPasswordStrength:
    """Tests for password strength scoring."""

    # TODO: Implement a strength scoring function and test it
    # Score could be 0-4 based on: length, uppercase, lowercase, digit, special

    def test_strength_scoring(self) -> None:
        """Test password strength scoring."""
        pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

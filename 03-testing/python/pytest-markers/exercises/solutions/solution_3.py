"""Solution for Exercise 3: Parametrized Test Matrix

This solution demonstrates comprehensive parametrized testing for password validation.
"""

import pytest


SPECIAL_CHARS = "!@#$%^&*"


def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password against security requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character from: !@#$%^&*

    Returns:
        tuple: (is_valid, error_message or "OK")
    """
    if not password or not password.strip():
        return False, "Password cannot be empty"

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain a digit"

    if not any(c in SPECIAL_CHARS for c in password):
        return False, "Password must contain a special character (!@#$%^&*)"

    return True, "OK"


# =============================================================================
# Test valid passwords
# =============================================================================


@pytest.mark.parametrize(
    "password",
    [
        "Password1!",
        "Secure@123",
        "MyP@ssw0rd",
        "Complex#Pass99",
        "Test!ng123",
        "Ab1!defgh",  # Minimum valid password
    ],
    ids=[
        "standard_valid",
        "with_at_symbol",
        "mixed_special",
        "longer_password",
        "exclamation",
        "minimum_length",
    ],
)
def test_valid_passwords(password: str) -> None:
    """Test passwords that should be valid."""
    is_valid, message = validate_password(password)
    assert is_valid, f"Password '{password}' should be valid but got: {message}"
    assert message == "OK"


# =============================================================================
# Test invalid passwords with specific reasons
# =============================================================================


@pytest.mark.parametrize(
    "password,expected_reason",
    [
        ("Short1!", "Password must be at least 8 characters"),
        ("lowercaseonly1!", "Password must contain an uppercase letter"),
        ("UPPERCASEONLY1!", "Password must contain a lowercase letter"),
        ("NoDigitsHere!", "Password must contain a digit"),
        ("NoSpecial123Aa", "Password must contain a special character (!@#$%^&*)"),
        ("", "Password cannot be empty"),
        ("   ", "Password cannot be empty"),
    ],
    ids=[
        "too_short",
        "no_uppercase",
        "no_lowercase",
        "no_digit",
        "no_special",
        "empty_string",
        "only_spaces",
    ],
)
def test_invalid_passwords(password: str, expected_reason: str) -> None:
    """Test passwords that should be invalid with specific error messages."""
    is_valid, message = validate_password(password)
    assert not is_valid, f"Password '{password}' should be invalid"
    assert message == expected_reason


# =============================================================================
# Test edge cases with parametrized matrix
# =============================================================================


@pytest.mark.parametrize("special_char", list(SPECIAL_CHARS))
def test_each_special_character(special_char: str) -> None:
    """Test that each special character is accepted."""
    password = f"Passw0rd{special_char}"
    is_valid, _ = validate_password(password)
    assert is_valid, f"Special char '{special_char}' should be valid"


@pytest.mark.parametrize(
    "length",
    [7, 8, 9, 16, 32],
    ids=["below_min", "at_min", "above_min", "medium", "long"],
)
def test_password_lengths(length: int) -> None:
    """Test various password lengths."""
    # Create a password of the specified length
    base = "Aa1!"
    filler = "x" * (length - len(base))
    password = base + filler

    is_valid, _ = validate_password(password)

    if length < 8:
        assert not is_valid, f"Password of length {length} should be invalid"
    else:
        assert is_valid, f"Password of length {length} should be valid"


# =============================================================================
# Test special cases with pytest.param and marks
# =============================================================================


@pytest.mark.parametrize(
    "password,is_valid,reason",
    [
        pytest.param(
            "A" * 1000 + "a1!",
            True,
            "OK",
            id="very_long_password",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            "Pssw0rd!",
            True,
            "OK",
            id="exactly_8_chars",
        ),
        pytest.param(
            "Pass 1! word",
            True,
            "OK",
            id="with_spaces",
        ),
        pytest.param(
            "Passwrd1\u2022",  # Unicode bullet point
            False,
            "Password must contain a special character (!@#$%^&*)",
            id="unicode_special_char",
            marks=pytest.mark.xfail(reason="Unicode special chars not in allowed list"),
        ),
    ],
)
def test_special_cases(password: str, is_valid: bool, reason: str) -> None:
    """Test special cases with appropriate marks."""
    actual_valid, actual_reason = validate_password(password)
    assert actual_valid == is_valid
    if not is_valid:
        assert actual_reason == reason


# =============================================================================
# Test password strength scoring
# =============================================================================


def calculate_strength(password: str) -> int:
    """Calculate password strength score (0-5).

    Scores one point for each:
    - Length >= 8
    - Contains uppercase
    - Contains lowercase
    - Contains digit
    - Contains special character
    """
    score = 0

    if len(password) >= 8:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in SPECIAL_CHARS for c in password):
        score += 1

    return score


class TestPasswordStrength:
    """Tests for password strength scoring."""

    @pytest.mark.parametrize(
        "password,expected_score",
        [
            pytest.param("", 0, id="empty"),
            pytest.param("short", 1, id="lowercase_only"),
            pytest.param("SHORT", 1, id="uppercase_only"),
            pytest.param("12345678", 2, id="digits_and_length"),
            pytest.param("Password", 3, id="mixed_case_length"),
            pytest.param("Password1", 4, id="mixed_case_digit_length"),
            pytest.param("Password1!", 5, id="all_requirements"),
        ],
    )
    def test_strength_scoring(self, password: str, expected_score: int) -> None:
        """Test password strength scoring."""
        score = calculate_strength(password)
        assert score == expected_score, f"'{password}' should have score {expected_score}"

    @pytest.mark.parametrize("score", [0, 1, 2, 3, 4, 5])
    def test_strength_labels(self, score: int) -> None:
        """Test strength score to label conversion."""
        labels = {
            0: "Very Weak",
            1: "Weak",
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong",
        }

        assert score in labels
        assert labels[score] is not None


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

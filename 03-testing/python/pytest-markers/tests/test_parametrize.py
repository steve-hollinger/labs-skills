"""Tests demonstrating @pytest.mark.parametrize.

This module shows various parametrization patterns including
basic usage, custom IDs, nested parametrize, and pytest.param.
"""

from dataclasses import dataclass

import pytest


# =============================================================================
# Basic Parametrization
# =============================================================================


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (-1, 1),
        (-2, 4),
        (0, 0),
    ],
)
def test_square(input_value: int, expected: int) -> None:
    """Test squaring integers with various inputs."""
    assert input_value**2 == expected


@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("hello", "HELLO"),
        ("World", "WORLD"),
        ("PyTest", "PYTEST"),
        ("", ""),
        ("123abc", "123ABC"),
    ],
)
def test_uppercase(input_string: str, expected: str) -> None:
    """Test string uppercase conversion."""
    assert input_string.upper() == expected


# =============================================================================
# Custom Test IDs
# =============================================================================


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 1),
        (2, 4),
        (3, 9),
    ],
    ids=["one_squared", "two_squared", "three_squared"],
)
def test_square_with_ids(input_value: int, expected: int) -> None:
    """Test with custom IDs for better readability."""
    assert input_value**2 == expected


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "admin@test.org",
        "support@company.io",
        "invalid",
    ],
    ids=lambda e: e.split("@")[-1] if "@" in e else "no_domain",
)
def test_email_validation(email: str) -> None:
    """Test email validation with dynamic IDs."""

    def is_valid_email(e: str) -> bool:
        return "@" in e and "." in e.split("@")[-1]

    if email == "invalid":
        assert not is_valid_email(email)
    else:
        assert is_valid_email(email)


# =============================================================================
# Multiple Parameters
# =============================================================================


@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", [10, 20])
def test_multiplication_matrix(a: int, b: int) -> None:
    """Test multiplication with cartesian product of inputs.

    This generates 6 tests: (1,10), (1,20), (2,10), (2,20), (3,10), (3,20)
    """
    result = a * b
    assert result == a * b
    assert result > 0


@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
@pytest.mark.parametrize("status_code", [200, 404, 500])
def test_http_response_handling(method: str, status_code: int) -> None:
    """Test HTTP response handling for different methods and status codes.

    This generates 9 tests (3 methods x 3 status codes).
    """

    def handle_response(m: str, s: int) -> str:
        if s == 200:
            return f"{m}: Success"
        elif s == 404:
            return f"{m}: Not Found"
        else:
            return f"{m}: Error"

    result = handle_response(method, status_code)
    assert method in result


# =============================================================================
# pytest.param with Marks
# =============================================================================


@pytest.mark.parametrize(
    "value,expected",
    [
        pytest.param(1, 1, id="positive"),
        pytest.param(-1, 1, id="negative"),
        pytest.param(0, 0, id="zero"),
        pytest.param(
            1000000,
            1000000000000,
            id="large_number",
            marks=pytest.mark.slow,
        ),
    ],
)
def test_square_with_param(value: int, expected: int) -> None:
    """Test using pytest.param for per-case configuration."""
    assert value**2 == expected


@pytest.mark.parametrize(
    "numerator,denominator,expected",
    [
        pytest.param(10, 2, 5, id="even_division"),
        pytest.param(10, 3, 3.333, id="decimal_result"),
        pytest.param(
            10,
            0,
            None,
            id="division_by_zero",
            marks=pytest.mark.xfail(raises=ZeroDivisionError),
        ),
        pytest.param(
            0,
            5,
            0,
            id="zero_numerator",
        ),
    ],
)
def test_division(numerator: int, denominator: int, expected: float | None) -> None:
    """Test division with xfail for division by zero."""
    result = numerator / denominator
    if isinstance(expected, float):
        assert abs(result - expected) < 0.01
    else:
        assert result == expected


# =============================================================================
# Complex Objects as Parameters
# =============================================================================


@dataclass
class ValidationTestCase:
    """Test case for validation tests."""

    name: str
    input_data: dict[str, str]
    is_valid: bool
    error_message: str | None = None


VALIDATION_CASES = [
    ValidationTestCase(
        name="valid_user",
        input_data={"email": "test@example.com", "name": "Test User"},
        is_valid=True,
    ),
    ValidationTestCase(
        name="missing_email",
        input_data={"name": "Test User"},
        is_valid=False,
        error_message="email is required",
    ),
    ValidationTestCase(
        name="missing_name",
        input_data={"email": "test@example.com"},
        is_valid=False,
        error_message="name is required",
    ),
    ValidationTestCase(
        name="empty_data",
        input_data={},
        is_valid=False,
        error_message="email is required",
    ),
]


@pytest.mark.parametrize("case", VALIDATION_CASES, ids=lambda c: c.name)
def test_user_validation(case: ValidationTestCase) -> None:
    """Test user validation with dataclass test cases."""

    def validate_user(data: dict[str, str]) -> tuple[bool, str | None]:
        if "email" not in data:
            return False, "email is required"
        if "name" not in data:
            return False, "name is required"
        return True, None

    is_valid, error = validate_user(case.input_data)
    assert is_valid == case.is_valid
    assert error == case.error_message


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


@pytest.mark.parametrize(
    "input_list,expected_length",
    [
        ([], 0),
        ([1], 1),
        ([1, 2, 3], 3),
        (list(range(100)), 100),
    ],
    ids=["empty", "single", "three_items", "hundred_items"],
)
def test_list_length(input_list: list[int], expected_length: int) -> None:
    """Test list length calculation."""
    assert len(input_list) == expected_length


@pytest.mark.parametrize(
    "input_value",
    [
        pytest.param(None, id="none"),
        pytest.param("", id="empty_string"),
        pytest.param(0, id="zero"),
        pytest.param(False, id="false"),
        pytest.param([], id="empty_list"),
    ],
)
def test_falsy_values(input_value: object) -> None:
    """Test handling of falsy values."""
    assert not input_value


# =============================================================================
# Parametrize in Test Class
# =============================================================================


class TestStringOperations:
    """Test class with parametrized methods."""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello", "olleh"),
            ("Python", "nohtyP"),
            ("a", "a"),
            ("", ""),
        ],
    )
    def test_reverse(self, input_str: str, expected: str) -> None:
        """Test string reversal."""
        assert input_str[::-1] == expected

    @pytest.mark.parametrize(
        "input_str,substr,expected",
        [
            ("hello world", "world", True),
            ("hello world", "foo", False),
            ("", "", True),
            ("test", "", True),
        ],
    )
    def test_contains(self, input_str: str, substr: str, expected: bool) -> None:
        """Test substring search."""
        assert (substr in input_str) == expected

"""Example 3: Parametrize Marker

This example demonstrates @pytest.mark.parametrize for data-driven testing,
including basic usage, custom IDs, nested parametrization, and advanced patterns.
"""


def main() -> None:
    """Demonstrate pytest parametrize marker."""
    print("Example 3: Parametrize Marker")
    print("=" * 50)
    print()

    # Basic parametrization
    print("1. Basic Parametrization")
    print("-" * 40)
    print("""
    import pytest

    @pytest.mark.parametrize("input,expected", [
        (1, 1),
        (2, 4),
        (3, 9),
        (4, 16),
        (-1, 1),
        (0, 0),
    ])
    def test_square(input, expected):
        assert input ** 2 == expected

    # Generates 6 tests:
    # test_square[1-1]
    # test_square[2-4]
    # test_square[3-9]
    # test_square[4-16]
    # test_square[-1-1]
    # test_square[0-0]
    """)

    # Custom IDs
    print("2. Custom Test IDs")
    print("-" * 40)
    print("""
    @pytest.mark.parametrize("input,expected", [
        (1, 1),
        (2, 4),
        (3, 9),
    ], ids=["one_squared", "two_squared", "three_squared"])
    def test_square_named(input, expected):
        assert input ** 2 == expected

    # Generates tests with readable names:
    # test_square_named[one_squared]
    # test_square_named[two_squared]
    # test_square_named[three_squared]

    # Dynamic IDs with lambda
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "admin@test.org",
        "support@company.io",
    ], ids=lambda e: e.split("@")[1])  # Use domain as ID
    def test_email_domain(email):
        assert "@" in email

    # test_email_domain[example.com]
    # test_email_domain[test.org]
    # test_email_domain[company.io]
    """)

    # Multiple parameters
    print("3. Nested Parametrization (Cartesian Product)")
    print("-" * 40)
    print("""
    @pytest.mark.parametrize("x", [1, 2, 3])
    @pytest.mark.parametrize("y", [10, 20])
    def test_multiplication(x, y):
        assert x * y == x * y

    # Generates 6 tests (3 x 2 = 6):
    # test_multiplication[10-1]   # y=10, x=1
    # test_multiplication[10-2]   # y=10, x=2
    # test_multiplication[10-3]   # y=10, x=3
    # test_multiplication[20-1]   # y=20, x=1
    # test_multiplication[20-2]   # y=20, x=2
    # test_multiplication[20-3]   # y=20, x=3

    # With three parameters (3 x 2 x 2 = 12 tests!)
    @pytest.mark.parametrize("method", ["GET", "POST"])
    @pytest.mark.parametrize("status", [200, 404])
    @pytest.mark.parametrize("format", ["json", "xml", "csv"])
    def test_api_response(method, status, format):
        pass
    """)

    # pytest.param for per-case marks
    print("4. pytest.param with Marks")
    print("-" * 40)
    print("""
    import pytest

    @pytest.mark.parametrize("value,expected", [
        pytest.param(1, 1, id="positive"),
        pytest.param(-1, 1, id="negative"),
        pytest.param(0, 0, id="zero"),
        pytest.param(
            None, 0,
            id="none_input",
            marks=pytest.mark.xfail(reason="None not handled")
        ),
        pytest.param(
            "string", 0,
            id="invalid_type",
            marks=pytest.mark.skip(reason="Type validation TODO")
        ),
        pytest.param(
            10**100, 10**200,
            id="large_number",
            marks=pytest.mark.slow
        ),
    ])
    def test_square_with_marks(value, expected):
        assert value ** 2 == expected
    """)

    # Parametrize with fixtures
    print("5. Parametrize with Fixtures")
    print("-" * 40)
    print("""
    import pytest

    @pytest.fixture
    def database_connection():
        conn = create_connection()
        yield conn
        conn.close()

    # Indirect parametrization - passes params to fixture
    @pytest.fixture
    def user(request):
        \"\"\"Create user with role from parameter.\"\"\"
        role = request.param
        return User(role=role)

    @pytest.mark.parametrize("user", ["admin", "editor", "viewer"], indirect=True)
    def test_user_permissions(user):
        if user.role == "admin":
            assert user.can_delete()
        elif user.role == "editor":
            assert user.can_edit()
        else:
            assert user.can_view()
    """)

    # Complex objects as parameters
    print("6. Complex Objects as Parameters")
    print("-" * 40)
    print("""
    from dataclasses import dataclass

    @dataclass
    class TestCase:
        name: str
        input: dict
        expected: dict
        should_fail: bool = False

    TEST_CASES = [
        TestCase(
            name="valid_user",
            input={"email": "test@example.com", "name": "Test"},
            expected={"status": "success"},
        ),
        TestCase(
            name="missing_email",
            input={"name": "Test"},
            expected={"error": "email required"},
            should_fail=True,
        ),
        TestCase(
            name="invalid_email",
            input={"email": "not-an-email", "name": "Test"},
            expected={"error": "invalid email"},
            should_fail=True,
        ),
    ]

    @pytest.mark.parametrize("case", TEST_CASES, ids=lambda c: c.name)
    def test_user_validation(case):
        result = validate_user(case.input)
        assert result == case.expected
    """)

    print()
    print("Run the tests to see parametrize in action:")
    print("  pytest tests/test_parametrize.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

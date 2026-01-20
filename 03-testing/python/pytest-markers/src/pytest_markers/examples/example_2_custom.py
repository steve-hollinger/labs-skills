"""Example 2: Custom Markers

This example demonstrates how to create and use custom markers for
organizing and categorizing tests in your test suite.
"""


def main() -> None:
    """Demonstrate custom pytest markers."""
    print("Example 2: Custom Markers")
    print("=" * 50)
    print()

    # Registering markers
    print("1. Registering Custom Markers")
    print("-" * 40)
    print("""
    In pyproject.toml:

    [tool.pytest.ini_options]
    markers = [
        "slow: marks tests as slow running (> 1 second)",
        "fast: marks tests as fast (< 100ms)",
        "unit: marks unit tests (isolated, no I/O)",
        "integration: marks integration tests (external deps)",
        "database: marks tests requiring database",
        "api: marks tests requiring API access",
        "smoke: marks smoke tests for quick validation",
    ]

    Without registration, pytest shows warnings:
    PytestUnknownMarkWarning: Unknown pytest.mark.slow
    """)

    # Using custom markers
    print("2. Applying Custom Markers")
    print("-" * 40)
    print("""
    import pytest

    @pytest.mark.unit
    def test_calculate_discount():
        \"\"\"Fast, isolated unit test.\"\"\"
        assert calculate_discount(100, 0.1) == 90

    @pytest.mark.slow
    @pytest.mark.integration
    def test_full_checkout_flow():
        \"\"\"Slow integration test hitting multiple services.\"\"\"
        cart = create_cart()
        cart.add_item(product)
        order = cart.checkout()
        assert order.status == "confirmed"

    @pytest.mark.database
    def test_user_persistence():
        \"\"\"Requires database connection.\"\"\"
        user = User.create(name="Test")
        loaded = User.get(user.id)
        assert loaded.name == "Test"
    """)

    # Running with markers
    print("3. Running Tests by Marker")
    print("-" * 40)
    print("""
    # Run only unit tests
    pytest -m unit

    # Run only slow tests
    pytest -m slow

    # Run everything EXCEPT slow tests
    pytest -m "not slow"

    # Run database OR api tests
    pytest -m "database or api"

    # Run integration tests that are NOT slow
    pytest -m "integration and not slow"

    # Complex expression
    pytest -m "(unit or smoke) and not database"
    """)

    # Module and class level markers
    print("4. Module and Class Level Markers")
    print("-" * 40)
    print("""
    # Module level - applies to ALL tests in file
    # tests/test_database.py
    import pytest

    pytestmark = pytest.mark.database  # Single marker

    # Or multiple markers
    pytestmark = [
        pytest.mark.database,
        pytest.mark.integration,
    ]

    def test_create_user():
        pass  # Has @database and @integration

    def test_delete_user():
        pass  # Has @database and @integration


    # Class level - applies to all methods
    @pytest.mark.slow
    class TestComplexAlgorithms:
        def test_sorting(self):
            pass  # Has @slow

        def test_searching(self):
            pass  # Has @slow

        @pytest.mark.xfail(reason="Not optimized")
        def test_optimization(self):
            pass  # Has @slow AND @xfail
    """)

    # Practical organization example
    print("5. Real-World Test Organization")
    print("-" * 40)
    print("""
    # Project structure:
    tests/
    ├── unit/
    │   └── test_models.py      # pytestmark = pytest.mark.unit
    ├── integration/
    │   ├── test_database.py    # pytestmark = [integration, database]
    │   └── test_api.py         # pytestmark = [integration, api]
    └── e2e/
        └── test_workflows.py   # pytestmark = [e2e, slow]

    # CI Pipeline:
    # Stage 1: pytest -m "unit" --timeout=10
    # Stage 2: pytest -m "integration and not slow"
    # Stage 3: pytest -m "slow or e2e"

    # Local development:
    # pytest -m "not slow and not e2e"  # Fast feedback
    """)

    print()
    print("Run the tests to see custom markers in action:")
    print("  pytest tests/test_custom_markers.py -v")
    print("  pytest tests/ -v -m slow")
    print("  pytest tests/ -v -m 'not slow'")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

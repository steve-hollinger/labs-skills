"""Example 4: Marker Combinations and Advanced Patterns

This example demonstrates advanced marker usage including combining markers,
marker expressions, conftest patterns, and dynamic marker assignment.
"""


def main() -> None:
    """Demonstrate advanced marker combinations."""
    print("Example 4: Marker Combinations and Advanced Patterns")
    print("=" * 50)
    print()

    # Combining multiple markers
    print("1. Combining Multiple Markers")
    print("-" * 40)
    print("""
    import pytest

    # Tests can have multiple markers
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.database
    def test_full_data_sync():
        \"\"\"Slow integration test requiring database.\"\"\"
        sync_all_data()
        assert verify_sync()

    # Stacking with other decorators
    @pytest.mark.unit
    @pytest.mark.fast
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_calculation(value):
        assert value > 0

    # Order doesn't matter
    @pytest.mark.database
    @pytest.mark.slow
    # Same as:
    @pytest.mark.slow
    @pytest.mark.database
    """)

    # Marker expressions
    print("2. Complex Marker Expressions")
    print("-" * 40)
    print("""
    # Run fast OR unit tests
    pytest -m "fast or unit"

    # Run database tests that are NOT slow
    pytest -m "database and not slow"

    # Run either (unit tests) or (fast integration tests)
    pytest -m "unit or (integration and fast)"

    # Exclude multiple markers
    pytest -m "not (slow or flaky or integration)"

    # Very specific selection
    pytest -m "(api and database) or smoke"

    # Useful CI expressions:
    # Quick validation: pytest -m "smoke"
    # Pre-commit hook: pytest -m "unit and fast"
    # Full CI: pytest -m "not flaky"
    # Nightly: pytest  # Everything
    """)

    # conftest.py patterns
    print("3. conftest.py Marker Patterns")
    print("-" * 40)
    print("""
    # conftest.py

    import pytest
    import os

    def pytest_configure(config):
        \"\"\"Register dynamic markers.\"\"\"
        config.addinivalue_line(
            "markers", "requires_env(name): skip if env var not set"
        )
        config.addinivalue_line(
            "markers", "min_python(version): skip if Python < version"
        )


    def pytest_collection_modifyitems(config, items):
        \"\"\"Modify collected tests based on markers.\"\"\"
        for item in items:
            # Auto-add 'unit' marker to tests without markers
            if not list(item.iter_markers()):
                item.add_marker(pytest.mark.unit)

            # Handle requires_env marker
            for marker in item.iter_markers(name="requires_env"):
                env_name = marker.args[0]
                if not os.environ.get(env_name):
                    item.add_marker(pytest.mark.skip(
                        reason=f"Environment variable {env_name} not set"
                    ))


    # Usage in tests:
    @pytest.mark.requires_env("DATABASE_URL")
    def test_database_connection():
        pass  # Skipped if DATABASE_URL not set

    @pytest.mark.requires_env("API_KEY")
    def test_external_api():
        pass  # Skipped if API_KEY not set
    """)

    # Dynamic markers in fixtures
    print("4. Dynamic Marker Handling in Fixtures")
    print("-" * 40)
    print("""
    import pytest

    @pytest.fixture(autouse=True)
    def handle_slow_tests(request):
        \"\"\"Add timeout handling for slow-marked tests.\"\"\"
        marker = request.node.get_closest_marker("slow")
        if marker:
            # Could set a longer timeout, allocate more resources, etc.
            print(f"Running slow test: {request.node.name}")
            yield
            print(f"Slow test completed: {request.node.name}")
        else:
            yield


    @pytest.fixture(autouse=True)
    def skip_integration_without_flag(request):
        \"\"\"Skip integration tests unless --run-integration flag.\"\"\"
        if request.node.get_closest_marker("integration"):
            if not request.config.getoption("--run-integration", default=False):
                pytest.skip("Integration tests disabled (use --run-integration)")
        yield


    # conftest.py addition for custom flag
    def pytest_addoption(parser):
        parser.addoption(
            "--run-integration",
            action="store_true",
            default=False,
            help="Run integration tests"
        )
    """)

    # Marker inheritance
    print("5. Marker Inheritance Patterns")
    print("-" * 40)
    print("""
    import pytest

    # Base test class with marker
    @pytest.mark.integration
    class TestIntegrationBase:
        \"\"\"Base class for all integration tests.\"\"\"

        @pytest.fixture(autouse=True)
        def setup_integration(self):
            # Common setup for integration tests
            self.client = create_test_client()
            yield
            self.client.cleanup()


    class TestUserAPI(TestIntegrationBase):
        \"\"\"Inherits @integration marker.\"\"\"

        def test_create_user(self):
            # Has @integration from parent
            response = self.client.post("/users", json={"name": "Test"})
            assert response.status_code == 201

        @pytest.mark.slow
        def test_bulk_import(self):
            # Has both @integration (inherited) and @slow
            pass


    # Module-level inheritance with class override
    pytestmark = pytest.mark.database

    @pytest.mark.api  # Additional marker
    class TestDatabaseAPI:
        def test_query(self):
            # Has both @database (module) and @api (class)
            pass
    """)

    # Practical workflow example
    print("6. Complete Workflow Example")
    print("-" * 40)
    print("""
    # pyproject.toml configuration
    [tool.pytest.ini_options]
    markers = [
        "smoke: Quick sanity checks (< 10 seconds total)",
        "unit: Isolated unit tests (no I/O)",
        "integration: Tests with external dependencies",
        "slow: Long-running tests (> 5 seconds each)",
        "flaky: Tests that occasionally fail",
        "wip: Work in progress tests",
    ]

    # CI Pipeline (.github/workflows/test.yml)
    jobs:
      smoke:
        runs-on: ubuntu-latest
        steps:
          - run: pytest -m smoke --timeout=30

      unit:
        needs: smoke
        runs-on: ubuntu-latest
        steps:
          - run: pytest -m "unit and not slow" --timeout=60

      integration:
        needs: unit
        runs-on: ubuntu-latest
        steps:
          - run: pytest -m "integration and not flaky" --timeout=300

      full:
        needs: integration
        runs-on: ubuntu-latest
        steps:
          - run: pytest -m "not wip" --timeout=600


    # Developer workflow
    # Quick check before commit:
    pytest -m "smoke or (unit and not slow)"

    # Full local validation:
    pytest -m "not (flaky or wip)"

    # Debug specific test:
    pytest -m "unit" -k "test_calculation" -v
    """)

    print()
    print("Run the tests to see marker combinations:")
    print("  pytest tests/ -v -m 'unit'")
    print("  pytest tests/ -v -m 'not slow'")
    print("  pytest tests/ -v -m 'integration and database'")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

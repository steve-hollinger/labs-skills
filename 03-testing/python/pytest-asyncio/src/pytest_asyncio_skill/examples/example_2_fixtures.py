"""Example 2: Async Fixtures

This example demonstrates how to create and use async fixtures
for setup and teardown of async resources.
"""

import asyncio
from dataclasses import dataclass, field


@dataclass
class AsyncDatabase:
    """Simulated async database connection."""

    name: str
    connected: bool = False
    data: dict[str, dict[str, str]] = field(default_factory=dict)

    async def connect(self) -> None:
        """Establish database connection."""
        await asyncio.sleep(0.01)  # Simulate connection time
        self.connected = True
        print(f"Database '{self.name}' connected")

    async def disconnect(self) -> None:
        """Close database connection."""
        await asyncio.sleep(0.01)  # Simulate disconnect time
        self.connected = False
        print(f"Database '{self.name}' disconnected")

    async def insert(self, table: str, record: dict[str, str]) -> str:
        """Insert a record into a table."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        await asyncio.sleep(0.01)  # Simulate insert time
        record_id = f"{table}_{len(self.data.get(table, {})) + 1}"
        if table not in self.data:
            self.data[table] = {}
        self.data[table][record_id] = record
        return record_id

    async def query(self, table: str, record_id: str) -> dict[str, str] | None:
        """Query a record from a table."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        await asyncio.sleep(0.01)  # Simulate query time
        return self.data.get(table, {}).get(record_id)


@dataclass
class AsyncHTTPClient:
    """Simulated async HTTP client."""

    base_url: str
    session_active: bool = False

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry."""
        await asyncio.sleep(0.01)  # Simulate session creation
        self.session_active = True
        print(f"HTTP session started for {self.base_url}")
        return self

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object) -> None:
        """Async context manager exit."""
        await asyncio.sleep(0.01)  # Simulate session cleanup
        self.session_active = False
        print(f"HTTP session closed for {self.base_url}")

    async def get(self, path: str) -> dict[str, str | int]:
        """Simulate GET request."""
        if not self.session_active:
            raise RuntimeError("Session not active")
        await asyncio.sleep(0.01)  # Simulate request time
        return {"url": f"{self.base_url}{path}", "status": 200}


def main() -> None:
    """Demonstrate async fixtures usage."""
    print("Example 2: Async Fixtures")
    print("=" * 50)
    print()

    # Show basic async fixture
    print("1. Basic Async Fixture")
    print("-" * 40)
    print("""
    import pytest

    @pytest.fixture
    async def database():
        \"\"\"Async fixture with setup and teardown.\"\"\"
        # Setup
        db = AsyncDatabase(name="test_db")
        await db.connect()

        yield db  # Provide the fixture

        # Teardown
        await db.disconnect()


    async def test_database_insert(database):
        \"\"\"Test using the async database fixture.\"\"\"
        record_id = await database.insert("users", {"name": "Test"})
        result = await database.query("users", record_id)
        assert result["name"] == "Test"
    """)

    # Show fixture with context manager
    print("2. Async Fixture with Context Manager")
    print("-" * 40)
    print("""
    @pytest.fixture
    async def http_client():
        \"\"\"Async fixture using async context manager.\"\"\"
        async with AsyncHTTPClient("https://api.example.com") as client:
            yield client
        # Client automatically closed after yield


    async def test_http_client(http_client):
        \"\"\"Test using the HTTP client fixture.\"\"\"
        response = await http_client.get("/users")
        assert response["status"] == 200
    """)

    # Show fixture dependencies
    print("3. Fixture Dependencies")
    print("-" * 40)
    print("""
    @pytest.fixture
    async def database():
        db = AsyncDatabase(name="test_db")
        await db.connect()
        yield db
        await db.disconnect()


    @pytest.fixture
    async def user_repository(database):
        \"\"\"Fixture that depends on database fixture.\"\"\"
        # Create some initial data
        await database.insert("users", {"name": "Admin", "role": "admin"})
        return database


    async def test_user_repository(user_repository):
        \"\"\"Test with dependent fixtures.\"\"\"
        # user_repository has pre-populated data
        users = user_repository.data.get("users", {})
        assert len(users) == 1
    """)

    # Show scoped fixtures
    print("4. Scoped Async Fixtures")
    print("-" * 40)
    print("""
    # Function scope (default) - new instance per test
    @pytest.fixture
    async def function_scoped_db():
        db = AsyncDatabase(name="function_db")
        await db.connect()
        yield db
        await db.disconnect()


    # Module scope - shared across all tests in module
    @pytest.fixture(scope="module")
    async def module_scoped_db():
        db = AsyncDatabase(name="module_db")
        await db.connect()
        yield db
        await db.disconnect()


    # Note: Module/session scoped fixtures need matching loop scope
    # Set in pyproject.toml: asyncio_default_fixture_loop_scope = "module"
    """)

    # Show multiple fixtures
    print("5. Multiple Async Fixtures")
    print("-" * 40)
    print("""
    @pytest.fixture
    async def database():
        db = AsyncDatabase(name="test_db")
        await db.connect()
        yield db
        await db.disconnect()


    @pytest.fixture
    async def http_client():
        async with AsyncHTTPClient("https://api.example.com") as client:
            yield client


    async def test_with_multiple_fixtures(database, http_client):
        \"\"\"Test using multiple async fixtures.\"\"\"
        # Both fixtures are ready to use
        assert database.connected
        assert http_client.session_active

        # Use them together
        response = await http_client.get("/health")
        await database.insert("logs", {"response": str(response)})
    """)

    # Demo
    print("6. Running Async Fixtures (Demo)")
    print("-" * 40)

    async def demo() -> None:
        # Simulate fixture lifecycle
        print("Starting fixture setup...")

        db = AsyncDatabase(name="demo_db")
        await db.connect()

        async with AsyncHTTPClient("https://api.example.com") as client:
            print(f"Database connected: {db.connected}")
            print(f"HTTP session active: {client.session_active}")

            # Simulate test execution
            record_id = await db.insert("users", {"name": "Demo User"})
            user = await db.query("users", record_id)
            print(f"Inserted and retrieved: {user}")

            response = await client.get("/users")
            print(f"HTTP response: {response}")

        print("HTTP session ended")
        await db.disconnect()
        print("Database disconnected")

    asyncio.run(demo())

    print()
    print("Run the tests with:")
    print("  pytest tests/test_async_fixtures.py -v")
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()

"""Tests demonstrating async fixtures with pytest-asyncio."""

import asyncio
from dataclasses import dataclass, field

import pytest


# =============================================================================
# Async Resources to Use in Fixtures
# =============================================================================


@dataclass
class AsyncDatabase:
    """Simulated async database connection."""

    name: str
    connected: bool = False
    data: dict[str, dict[str, str]] = field(default_factory=dict)

    async def connect(self) -> None:
        """Establish database connection."""
        await asyncio.sleep(0.01)
        self.connected = True

    async def disconnect(self) -> None:
        """Close database connection."""
        await asyncio.sleep(0.01)
        self.connected = False

    async def insert(self, table: str, record: dict[str, str]) -> str:
        """Insert a record into a table."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        await asyncio.sleep(0.01)
        record_id = f"{table}_{len(self.data.get(table, {})) + 1}"
        if table not in self.data:
            self.data[table] = {}
        self.data[table][record_id] = record
        return record_id

    async def query(self, table: str, record_id: str) -> dict[str, str] | None:
        """Query a record from a table."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        await asyncio.sleep(0.01)
        return self.data.get(table, {}).get(record_id)


@dataclass
class AsyncHTTPClient:
    """Simulated async HTTP client."""

    base_url: str
    session_active: bool = False
    request_count: int = 0

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry."""
        await asyncio.sleep(0.01)
        self.session_active = True
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: object | None,
    ) -> None:
        """Async context manager exit."""
        await asyncio.sleep(0.01)
        self.session_active = False

    async def get(self, path: str) -> dict[str, str | int]:
        """Simulate GET request."""
        if not self.session_active:
            raise RuntimeError("Session not active")
        self.request_count += 1
        await asyncio.sleep(0.01)
        return {"url": f"{self.base_url}{path}", "status": 200}


# =============================================================================
# Async Fixtures
# =============================================================================


@pytest.fixture
async def database() -> AsyncDatabase:
    """Async fixture with setup and teardown."""
    db = AsyncDatabase(name="test_db")
    await db.connect()

    yield db

    await db.disconnect()


@pytest.fixture
async def http_client() -> AsyncHTTPClient:
    """Async fixture using async context manager."""
    async with AsyncHTTPClient("https://api.example.com") as client:
        yield client


@pytest.fixture
async def populated_database(database: AsyncDatabase) -> AsyncDatabase:
    """Fixture that depends on another async fixture."""
    await database.insert("users", {"name": "Admin", "role": "admin"})
    await database.insert("users", {"name": "User", "role": "user"})
    return database


# =============================================================================
# Tests Using Async Fixtures
# =============================================================================


async def test_database_connection(database: AsyncDatabase) -> None:
    """Test database fixture is connected."""
    assert database.connected is True
    assert database.name == "test_db"


async def test_database_insert_and_query(database: AsyncDatabase) -> None:
    """Test database operations."""
    record_id = await database.insert("users", {"name": "Test User"})
    result = await database.query("users", record_id)

    assert result is not None
    assert result["name"] == "Test User"


async def test_database_multiple_operations(database: AsyncDatabase) -> None:
    """Test multiple database operations."""
    # Insert multiple records
    id1 = await database.insert("products", {"name": "Widget"})
    id2 = await database.insert("products", {"name": "Gadget"})

    # Query them back
    product1 = await database.query("products", id1)
    product2 = await database.query("products", id2)

    assert product1 is not None and product1["name"] == "Widget"
    assert product2 is not None and product2["name"] == "Gadget"


async def test_http_client_session(http_client: AsyncHTTPClient) -> None:
    """Test HTTP client fixture has active session."""
    assert http_client.session_active is True


async def test_http_client_get(http_client: AsyncHTTPClient) -> None:
    """Test HTTP client GET request."""
    response = await http_client.get("/users")

    assert response["status"] == 200
    assert "/users" in response["url"]


async def test_http_client_multiple_requests(http_client: AsyncHTTPClient) -> None:
    """Test multiple HTTP requests."""
    await http_client.get("/users")
    await http_client.get("/products")
    await http_client.get("/orders")

    assert http_client.request_count == 3


# =============================================================================
# Tests with Dependent Fixtures
# =============================================================================


async def test_populated_database(populated_database: AsyncDatabase) -> None:
    """Test fixture with pre-populated data."""
    # Check that pre-populated data exists
    users = populated_database.data.get("users", {})
    assert len(users) == 2


async def test_populated_database_add_more(populated_database: AsyncDatabase) -> None:
    """Test adding to pre-populated database."""
    # Add a new user
    new_id = await populated_database.insert("users", {"name": "New User", "role": "guest"})

    # Should now have 3 users
    users = populated_database.data.get("users", {})
    assert len(users) == 3
    assert new_id in users


# =============================================================================
# Tests with Multiple Fixtures
# =============================================================================


async def test_multiple_fixtures(
    database: AsyncDatabase,
    http_client: AsyncHTTPClient,
) -> None:
    """Test using multiple async fixtures together."""
    assert database.connected
    assert http_client.session_active

    # Use both fixtures
    await http_client.get("/health")
    await database.insert("logs", {"event": "health_check"})

    assert http_client.request_count == 1
    assert "logs" in database.data


# =============================================================================
# Tests Verifying Fixture Lifecycle
# =============================================================================


async def test_fixture_isolation_1(database: AsyncDatabase) -> None:
    """First test - insert data."""
    await database.insert("test_table", {"value": "test1"})
    assert len(database.data["test_table"]) == 1


async def test_fixture_isolation_2(database: AsyncDatabase) -> None:
    """Second test - should have clean database.

    Each test gets a fresh fixture instance, so data from
    test_fixture_isolation_1 should not be present.
    """
    assert "test_table" not in database.data


class TestAsyncFixtureInClass:
    """Test class using async fixtures."""

    async def test_method_with_fixture(self, database: AsyncDatabase) -> None:
        """Test method using fixture."""
        assert database.connected

    async def test_another_method_with_fixture(
        self, http_client: AsyncHTTPClient
    ) -> None:
        """Another test method using different fixture."""
        response = await http_client.get("/test")
        assert response["status"] == 200

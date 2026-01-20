"""Solution for Exercise 2: Create Async Fixtures for Database Testing"""

import asyncio
from dataclasses import dataclass, field

import pytest


@dataclass
class AsyncDatabase:
    """Simulated async database."""

    name: str
    connected: bool = False
    data: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)

    async def connect(self) -> None:
        await asyncio.sleep(0.01)
        self.connected = True

    async def disconnect(self) -> None:
        await asyncio.sleep(0.01)
        self.connected = False

    async def insert(self, table: str, record_id: str, record: dict[str, str]) -> None:
        if not self.connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.01)
        if table not in self.data:
            self.data[table] = {}
        self.data[table][record_id] = record

    async def find(self, table: str, record_id: str) -> dict[str, str] | None:
        if not self.connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.01)
        return self.data.get(table, {}).get(record_id)

    async def find_all(self, table: str) -> list[dict[str, str]]:
        if not self.connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.01)
        return list(self.data.get(table, {}).values())

    async def delete(self, table: str, record_id: str) -> bool:
        if not self.connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.01)
        if table in self.data and record_id in self.data[table]:
            del self.data[table][record_id]
            return True
        return False


@dataclass
class User:
    """User model."""

    id: str
    name: str
    email: str


class UserRepository:
    """Repository for user operations."""

    def __init__(self, database: AsyncDatabase) -> None:
        self.db = database

    async def create(self, user: User) -> None:
        """Create a new user."""
        await self.db.insert(
            "users", user.id, {"id": user.id, "name": user.name, "email": user.email}
        )

    async def get(self, user_id: str) -> User | None:
        """Get user by ID."""
        record = await self.db.find("users", user_id)
        if record:
            return User(id=record["id"], name=record["name"], email=record["email"])
        return None

    async def get_all(self) -> list[User]:
        """Get all users."""
        records = await self.db.find_all("users")
        return [User(id=r["id"], name=r["name"], email=r["email"]) for r in records]

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        return await self.db.delete("users", user_id)


# =============================================================================
# Fixtures (Solutions)
# =============================================================================


@pytest.fixture
async def database() -> AsyncDatabase:
    """Create an async database connection."""
    db = AsyncDatabase(name="test_db")
    await db.connect()

    yield db

    await db.disconnect()


@pytest.fixture
async def user_repository(database: AsyncDatabase) -> UserRepository:
    """Create a UserRepository with the database fixture."""
    return UserRepository(database)


@pytest.fixture
async def seeded_database(database: AsyncDatabase) -> AsyncDatabase:
    """Database pre-populated with test users."""
    await database.insert(
        "users", "user1", {"id": "user1", "name": "Alice", "email": "alice@example.com"}
    )
    await database.insert(
        "users", "user2", {"id": "user2", "name": "Bob", "email": "bob@example.com"}
    )
    return database


# =============================================================================
# Tests (Solutions)
# =============================================================================


async def test_database_connects(database: AsyncDatabase) -> None:
    """Test that database fixture provides a connected database."""
    assert database.connected is True
    assert database.name == "test_db"


async def test_create_user(user_repository: UserRepository) -> None:
    """Test creating a user through the repository."""
    user = User(id="u1", name="Test User", email="test@example.com")
    await user_repository.create(user)

    retrieved = await user_repository.get("u1")

    assert retrieved is not None
    assert retrieved.id == "u1"
    assert retrieved.name == "Test User"
    assert retrieved.email == "test@example.com"


async def test_get_nonexistent_user(user_repository: UserRepository) -> None:
    """Test getting a user that doesn't exist."""
    result = await user_repository.get("nonexistent")
    assert result is None


async def test_seeded_database_has_users(seeded_database: AsyncDatabase) -> None:
    """Test that seeded database has pre-populated users."""
    repo = UserRepository(seeded_database)
    users = await repo.get_all()

    assert len(users) == 2
    names = {u.name for u in users}
    assert names == {"Alice", "Bob"}


async def test_delete_user(user_repository: UserRepository) -> None:
    """Test deleting a user."""
    # Create a user
    user = User(id="del1", name="To Delete", email="delete@example.com")
    await user_repository.create(user)

    # Verify it exists
    assert await user_repository.get("del1") is not None

    # Delete it
    deleted = await user_repository.delete("del1")
    assert deleted is True

    # Verify it's gone
    assert await user_repository.get("del1") is None


async def test_fixture_isolation(database: AsyncDatabase) -> None:
    """Test that fixtures are isolated between tests."""
    # Insert data that should NOT affect other tests
    await database.insert(
        "isolation_test",
        "record1",
        {"data": "should not persist"},
    )

    # Verify data exists in this test
    record = await database.find("isolation_test", "record1")
    assert record is not None


async def test_fixture_isolation_verification(database: AsyncDatabase) -> None:
    """Verify isolation - data from previous test should not exist."""
    # If fixtures are properly isolated, this table should not exist
    record = await database.find("isolation_test", "record1")
    assert record is None


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

"""Exercise 2: Create Async Fixtures for Database Testing

Your task is to create async fixtures for testing database operations
and use them to test the UserRepository class.

Instructions:
1. Implement the async fixtures marked with TODO
2. Implement the test functions using those fixtures
3. Ensure proper setup and teardown of resources

Expected Fixtures:
- database: Creates and connects an AsyncDatabase, yields it, then disconnects
- user_repository: Depends on database, provides UserRepository instance
- seeded_database: Pre-populates database with test users

Hints:
- Use async fixtures with yield for cleanup
- Fixtures can depend on other fixtures
- Remember to await async operations in fixtures

Run your tests with:
    pytest exercises/exercise_2.py -v
"""

import asyncio
from dataclasses import dataclass, field

import pytest  # noqa: F401


# =============================================================================
# Simulated Database and Repository
# =============================================================================


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
        return [
            User(id=r["id"], name=r["name"], email=r["email"]) for r in records
        ]

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        return await self.db.delete("users", user_id)


# =============================================================================
# TODO: Implement the fixtures below
# =============================================================================


@pytest.fixture
async def database():
    """Create an async database connection.

    TODO:
    1. Create an AsyncDatabase instance
    2. Connect to the database
    3. Yield the database for tests to use
    4. Disconnect when the test is done (cleanup)
    """
    pass


@pytest.fixture
async def user_repository(database):
    """Create a UserRepository with the database fixture.

    TODO:
    1. Create a UserRepository using the database fixture
    2. Return the repository
    """
    pass


@pytest.fixture
async def seeded_database(database):
    """Database pre-populated with test users.

    TODO:
    1. Use the database fixture
    2. Insert some test users (at least 2)
    3. Return the database
    """
    pass


# =============================================================================
# TODO: Implement the tests below
# =============================================================================


async def test_database_connects(database) -> None:
    """Test that database fixture provides a connected database.

    TODO: Verify the database is connected.
    """
    pass


async def test_create_user(user_repository) -> None:
    """Test creating a user through the repository.

    TODO:
    1. Create a User instance
    2. Save it using the repository
    3. Retrieve it and verify the data
    """
    pass


async def test_get_nonexistent_user(user_repository) -> None:
    """Test getting a user that doesn't exist.

    TODO: Verify that getting a nonexistent user returns None.
    """
    pass


async def test_seeded_database_has_users(seeded_database) -> None:
    """Test that seeded database has pre-populated users.

    TODO:
    1. Create a UserRepository with the seeded database
    2. Verify that get_all() returns the seeded users
    """
    pass


async def test_delete_user(user_repository) -> None:
    """Test deleting a user.

    TODO:
    1. Create and save a user
    2. Delete the user
    3. Verify the user is gone
    """
    pass


async def test_fixture_isolation(database) -> None:
    """Test that fixtures are isolated between tests.

    TODO:
    1. Insert some data into the database
    2. Verify the data exists in this test
    (The next test should NOT see this data - fixtures are recreated)
    """
    pass


if __name__ == "__main__":
    import subprocess

    subprocess.run(["pytest", __file__, "-v"])

"""Example 2: Component Dependencies

This example demonstrates how components can depend on other components.
The dependency injection system automatically resolves dependencies and
ensures they're initialized before the dependent component.

Key concepts:
- Declaring dependencies with Requires()
- Automatic dependency injection
- Proper initialization order
- Accessing injected dependencies
"""

import asyncio
from typing import Any, ClassVar

from component_system import Component, Registry, Requires


class DatabaseComponent(Component):
    """Simulated database component.

    In a real application, this would manage database connections
    and provide query methods.
    """

    name: ClassVar[str] = "database"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._connected = False
        self._data: dict[str, dict[str, Any]] = {}

    @property
    def connected(self) -> bool:
        """Check if database is connected."""
        return self._connected

    async def initialize(self) -> None:
        """Validate database configuration."""
        await super().initialize()
        required = ["host", "port", "database"]
        missing = [k for k in required if k not in self.config]
        if missing:
            # Use defaults for demo
            print(f"  [Database] Using default config (missing: {missing})")
        print("  [Database] Configuration validated")

    async def start(self) -> None:
        """Connect to the database."""
        await super().start()
        # Simulate connection
        await asyncio.sleep(0.1)
        self._connected = True
        print(f"  [Database] Connected to {self.config.get('host', 'localhost')}")

    async def stop(self) -> None:
        """Close database connection."""
        if self._connected:
            # Simulate disconnection
            await asyncio.sleep(0.05)
            self._connected = False
            print("  [Database] Connection closed")
        await super().stop()

    async def query(self, table: str, id: str) -> dict[str, Any] | None:
        """Query data by ID."""
        if not self._connected:
            raise RuntimeError("Database not connected")
        return self._data.get(table, {}).get(id)

    async def insert(self, table: str, id: str, data: dict[str, Any]) -> None:
        """Insert data."""
        if not self._connected:
            raise RuntimeError("Database not connected")
        if table not in self._data:
            self._data[table] = {}
        self._data[table][id] = data


class CacheComponent(Component):
    """In-memory cache component."""

    name: ClassVar[str] = "cache"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._cache: dict[str, Any] = {}
        self._ttl = 300  # 5 minutes default

    async def initialize(self) -> None:
        """Configure cache settings."""
        await super().initialize()
        self._ttl = self.config.get("ttl", 300)
        print(f"  [Cache] TTL set to {self._ttl} seconds")

    async def start(self) -> None:
        """Start cache service."""
        await super().start()
        print("  [Cache] Ready")

    async def stop(self) -> None:
        """Clear cache on shutdown."""
        self._cache.clear()
        print(f"  [Cache] Cleared {len(self._cache)} entries")
        await super().stop()

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value


class UserService(Component):
    """User service that depends on database and cache.

    This component demonstrates dependency injection:
    - It declares dependencies using Requires()
    - Dependencies are automatically injected before initialize()
    - The registry ensures dependencies start before this component
    """

    name: ClassVar[str] = "user-service"

    # Declare dependencies
    database: DatabaseComponent = Requires()
    cache: CacheComponent = Requires()

    async def initialize(self) -> None:
        """Initialize user service."""
        await super().initialize()
        # At this point, dependencies are injected and available
        print(f"  [UserService] Dependencies injected:")
        print(f"    - database: {self.database.name}")
        print(f"    - cache: {self.cache.name}")

    async def start(self) -> None:
        """Start user service."""
        await super().start()
        print("  [UserService] Ready to serve requests")

    async def stop(self) -> None:
        """Stop user service."""
        print("  [UserService] Shutting down")
        await super().stop()

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Get user by ID, using cache if available."""
        cache_key = f"user:{user_id}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"  [UserService] Cache hit for {user_id}")
            return cached  # type: ignore[return-value]

        # Query database
        print(f"  [UserService] Cache miss, querying database for {user_id}")
        user = await self.database.query("users", user_id)

        # Store in cache if found
        if user:
            await self.cache.set(cache_key, user)

        return user

    async def create_user(self, user_id: str, name: str, email: str) -> dict[str, Any]:
        """Create a new user."""
        user = {"id": user_id, "name": name, "email": email}
        await self.database.insert("users", user_id, user)
        await self.cache.set(f"user:{user_id}", user)
        print(f"  [UserService] Created user: {name}")
        return user


async def main() -> None:
    """Run the component dependencies example."""
    print("Example 2: Component Dependencies")
    print("=" * 50)

    # Create registry and register components
    registry = Registry()

    print("\n1. Registering components (in any order)...")
    # Note: We can register in any order - dependencies are resolved automatically
    registry.register(UserService)  # Depends on Database and Cache
    registry.register(CacheComponent, config={"ttl": 600})
    registry.register(DatabaseComponent, config={"host": "localhost", "port": 5432})

    # Start all - the registry figures out the correct order
    print("\n2. Starting all components (dependencies start first)...")
    await registry.start_all()

    # Use the service
    print("\n3. Using UserService:")
    user_service = registry.get(UserService)

    # Create some users
    await user_service.create_user("u1", "Alice", "alice@example.com")
    await user_service.create_user("u2", "Bob", "bob@example.com")

    # Get users (demonstrates cache usage)
    print("\n4. Fetching users (second fetch uses cache):")
    user1 = await user_service.get_user("u1")
    print(f"   Found: {user1}")

    user1_again = await user_service.get_user("u1")  # Cache hit
    print(f"   Found again: {user1_again}")

    user3 = await user_service.get_user("u3")  # Not found
    print(f"   Non-existent user: {user3}")

    # Stop all - dependencies stop in reverse order
    print("\n5. Stopping all components (dependents stop first)...")
    await registry.stop_all()

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

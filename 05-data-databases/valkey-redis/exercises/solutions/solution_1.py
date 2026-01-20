"""Solution 1: Cache Manager Implementation.

This is the solution for Exercise 1: Build a Cache Manager.
"""

from __future__ import annotations

import json
from typing import Any, Callable, TypeVar

import redis

T = TypeVar("T")


class CacheManager:
    """Generic cache manager with TTL support."""

    def __init__(
        self,
        client: redis.Redis[str],
        default_ttl: int = 3600,
        prefix: str = "cache",
    ) -> None:
        """Initialize cache manager."""
        self._client = client
        self._default_ttl = default_ttl
        self._prefix = prefix
        self._hits = 0
        self._misses = 0

    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix."""
        return f"{self._prefix}:{key}"

    def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        full_key = self._make_key(key)
        value = self._client.get(full_key)

        if value is not None:
            self._hits += 1
            return json.loads(value)
        else:
            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in cache."""
        full_key = self._make_key(key)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        self._client.setex(full_key, effective_ttl, json.dumps(value))

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        full_key = self._make_key(key)
        return self._client.delete(full_key) > 0

    def get_or_set(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        """Get from cache or fetch and cache."""
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        # Fetch and cache
        value = fetch_fn()
        self.set(key, value, ttl)
        return value

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        full_key = self._make_key(key)
        return self._client.exists(full_key) > 0

    def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        full_key = self._make_key(key)
        return self._client.ttl(full_key)

    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    @property
    def hits(self) -> int:
        """Get number of cache hits."""
        return self._hits

    @property
    def misses(self) -> int:
        """Get number of cache misses."""
        return self._misses

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._hits = 0
        self._misses = 0


def main() -> None:
    """Demonstrate the cache manager."""
    print("Solution 1: Cache Manager")
    print("=" * 40)

    # Connect to Redis
    try:
        client: redis.Redis[str] = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )
        client.ping()
        print("\n[OK] Connected to Valkey")
    except redis.ConnectionError as e:
        print(f"\n[ERROR] Could not connect: {e}")
        return

    # Clean up
    for key in client.scan_iter(match="cache:*"):
        client.delete(key)

    # Create cache manager with 60 second TTL
    cache = CacheManager(client, default_ttl=60, prefix="cache")

    print("\n--- Testing set() and get() ---")
    cache.set("user:1", {"name": "Alice", "age": 30})
    user = cache.get("user:1")
    print(f"  Set and retrieved user: {user}")
    print(f"  TTL: {cache.ttl('user:1')} seconds")

    print("\n--- Testing cache miss ---")
    result = cache.get("nonexistent")
    print(f"  Get nonexistent key: {result}")

    print("\n--- Testing get_or_set() ---")
    # First call - cache miss, will call fetch function
    fetch_count = 0

    def fetch_data() -> dict[str, Any]:
        nonlocal fetch_count
        fetch_count += 1
        print("  [Fetch function called]")
        return {"data": "expensive computation", "call": fetch_count}

    result1 = cache.get_or_set("expensive", fetch_data)
    print(f"  First call: {result1}")

    # Second call - cache hit
    result2 = cache.get_or_set("expensive", fetch_data)
    print(f"  Second call: {result2}")
    print(f"  Fetch function called {fetch_count} time(s)")

    print("\n--- Testing exists() and delete() ---")
    print(f"  Key exists before delete: {cache.exists('user:1')}")
    deleted = cache.delete("user:1")
    print(f"  Deleted: {deleted}")
    print(f"  Key exists after delete: {cache.exists('user:1')}")

    print("\n--- Statistics ---")
    print(f"  Hits: {cache.hits}")
    print(f"  Misses: {cache.misses}")
    print(f"  Hit rate: {cache.hit_rate():.1%}")

    # Clean up
    for key in client.scan_iter(match="cache:*"):
        client.delete(key)

    print("\n" + "=" * 40)
    print("Solution completed successfully!")


if __name__ == "__main__":
    main()

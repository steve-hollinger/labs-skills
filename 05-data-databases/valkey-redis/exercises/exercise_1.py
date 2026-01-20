"""Exercise 1: Build a Cache Manager.

In this exercise, you will create a generic cache manager class that
wraps common caching operations with TTL support.

Requirements:
1. Create a CacheManager class with:
   - Configurable default TTL
   - Key prefix support
   - JSON serialization/deserialization

2. Implement these methods:
   - get(key) -> Any | None
   - set(key, value, ttl=None)
   - delete(key) -> bool
   - get_or_set(key, fetch_fn, ttl=None)
   - exists(key) -> bool
   - ttl(key) -> int

3. Add statistics tracking:
   - hits: number of cache hits
   - misses: number of cache misses
   - hit_rate() -> float

Run with: python exercises/exercise_1.py
Test with: pytest tests/test_exercises.py -k exercise_1
"""

from __future__ import annotations

import json
from typing import Any, Callable, TypeVar

import redis

T = TypeVar("T")


class CacheManager:
    """Generic cache manager with TTL support.

    TODO: Implement this class with the following:
    - Constructor accepting client, default_ttl, and prefix
    - Statistics tracking (hits, misses)
    - All required methods
    """

    def __init__(
        self,
        client: redis.Redis[str],
        default_ttl: int = 3600,
        prefix: str = "cache",
    ) -> None:
        """Initialize cache manager.

        TODO:
        1. Store the client, default_ttl, and prefix
        2. Initialize hits and misses counters
        """
        pass

    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix.

        TODO: Return "{prefix}:{key}"
        """
        pass

    def get(self, key: str) -> Any | None:
        """Get a value from cache.

        TODO:
        1. Get value from Redis
        2. If found, increment hits and return deserialized value
        3. If not found, increment misses and return None
        """
        pass

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in cache.

        TODO:
        1. Serialize value to JSON
        2. Store with SETEX using ttl or default_ttl
        """
        pass

    def delete(self, key: str) -> bool:
        """Delete a key from cache.

        TODO: Delete and return True if key was deleted
        """
        pass

    def get_or_set(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        """Get from cache or fetch and cache.

        TODO:
        1. Try to get from cache
        2. If hit, return cached value
        3. If miss, call fetch_fn, cache result, and return
        """
        pass

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        TODO: Return True if key exists
        """
        pass

    def ttl(self, key: str) -> int:
        """Get remaining TTL for a key.

        TODO: Return TTL in seconds
        """
        pass

    def hit_rate(self) -> float:
        """Calculate cache hit rate.

        TODO: Return hits / (hits + misses), or 0.0 if no requests
        """
        pass


def main() -> None:
    """Demonstrate the cache manager."""
    print("Exercise 1: Cache Manager")
    print("=" * 40)

    # TODO: Implement the demonstration
    #
    # 1. Connect to Redis
    # 2. Create a CacheManager with 60 second TTL
    # 3. Test the following scenarios:
    #    a. set() and get() a simple value
    #    b. get() a non-existent key
    #    c. get_or_set() with a lambda
    #    d. delete() a key
    #    e. Print hit rate
    #
    # Expected output should show:
    # - Cache hits and misses
    # - Hit rate calculation
    # - TTL values

    print("\nNot implemented yet. See TODO comments.")


if __name__ == "__main__":
    main()

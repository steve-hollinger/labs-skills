"""Cache utilities and patterns."""

from __future__ import annotations

import functools
import hashlib
import json
import logging
import time
import uuid
from typing import Any, Callable, TypeVar

import redis

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheManager:
    """High-level cache manager with common patterns.

    Implements cache-aside pattern with optional locking for
    stampede protection.

    Example:
        >>> manager = CacheManager(client)
        >>> user = manager.get_or_set(
        ...     key="user:123",
        ...     fetch_fn=lambda: database.get_user(123),
        ...     ttl=3600
        ... )
    """

    def __init__(
        self,
        client: redis.Redis[str],
        default_ttl: int = 3600,
        key_prefix: str = "",
    ) -> None:
        """Initialize the cache manager.

        Args:
            client: Redis client instance.
            default_ttl: Default TTL in seconds.
            key_prefix: Prefix for all cache keys.
        """
        self._client = client
        self._default_ttl = default_ttl
        self._key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix."""
        if self._key_prefix:
            return f"{self._key_prefix}:{key}"
        return key

    def get(self, key: str) -> Any | None:
        """Get a value from cache.

        Args:
            key: Cache key.

        Returns:
            Deserialized value or None.
        """
        full_key = self._make_key(key)
        value = self._client.get(full_key)
        if value is not None:
            return json.loads(value)
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set a value in cache.

        Args:
            key: Cache key.
            value: Value to cache (will be JSON serialized).
            ttl: TTL in seconds (uses default if None).
        """
        full_key = self._make_key(key)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        self._client.setex(full_key, effective_ttl, json.dumps(value))

    def delete(self, key: str) -> bool:
        """Delete a key from cache.

        Args:
            key: Cache key.

        Returns:
            True if key was deleted.
        """
        full_key = self._make_key(key)
        return self._client.delete(full_key) > 0

    def get_or_set(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        """Get from cache or fetch and cache.

        Implements the cache-aside pattern.

        Args:
            key: Cache key.
            fetch_fn: Function to fetch value on cache miss.
            ttl: TTL in seconds.

        Returns:
            Cached or fetched value.
        """
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            logger.debug(f"Cache HIT: {key}")
            return cached  # type: ignore[return-value]

        # Cache miss - fetch from source
        logger.debug(f"Cache MISS: {key}")
        value = fetch_fn()

        # Store in cache
        self.set(key, value, ttl)

        return value

    def get_or_set_with_lock(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int | None = None,
        lock_timeout: int = 10,
    ) -> T | None:
        """Get from cache with lock protection.

        Prevents cache stampede by using distributed locking.

        Args:
            key: Cache key.
            fetch_fn: Function to fetch value on cache miss.
            ttl: TTL in seconds.
            lock_timeout: Lock timeout in seconds.

        Returns:
            Cached or fetched value, or None if lock timeout.
        """
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        # Try to acquire lock
        lock_key = f"lock:{self._make_key(key)}"
        lock_id = str(uuid.uuid4())

        if self._client.set(lock_key, lock_id, nx=True, ex=lock_timeout):
            try:
                # Double-check cache
                cached = self.get(key)
                if cached is not None:
                    return cached  # type: ignore[return-value]

                # Fetch and cache
                value = fetch_fn()
                self.set(key, value, ttl)
                return value
            finally:
                # Release lock if we own it
                self._release_lock(lock_key, lock_id)
        else:
            # Wait for lock holder
            for _ in range(lock_timeout * 10):
                time.sleep(0.1)
                cached = self.get(key)
                if cached is not None:
                    return cached  # type: ignore[return-value]
            logger.warning(f"Lock timeout waiting for: {key}")
            return None

    def _release_lock(self, key: str, lock_id: str) -> None:
        """Release lock only if we own it."""
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        self._client.eval(script, 1, key, lock_id)  # type: ignore[union-attr]

    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "user:*").

        Returns:
            Number of keys deleted.
        """
        full_pattern = self._make_key(pattern)
        keys = list(self._client.scan_iter(match=full_pattern))
        if keys:
            return self._client.delete(*keys)
        return 0


def cached(
    key_template: str,
    ttl: int = 3600,
    key_prefix: str = "cache",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for caching function results.

    Args:
        key_template: Key template with format placeholders.
        ttl: TTL in seconds.
        key_prefix: Prefix for cache keys.

    Returns:
        Decorator function.

    Example:
        >>> @cached(key_template="user:{user_id}", ttl=3600)
        ... def get_user(user_id: str) -> dict:
        ...     return database.get_user(user_id)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get client from first argument if it's a method
            # Otherwise, create a new client
            client = redis.Redis(decode_responses=True)

            # Build cache key from template and arguments
            # Get function argument names
            import inspect

            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Build key
            try:
                key = key_template.format(**bound.arguments)
            except KeyError:
                # Fallback to hash of arguments
                arg_hash = hashlib.md5(
                    json.dumps(bound.arguments, sort_keys=True, default=str).encode()
                ).hexdigest()[:8]
                key = f"{func.__name__}:{arg_hash}"

            full_key = f"{key_prefix}:{key}"

            # Try cache
            cached_value = client.get(full_key)
            if cached_value is not None:
                return json.loads(cached_value)  # type: ignore[return-value]

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            client.setex(full_key, ttl, json.dumps(result))

            return result

        return wrapper

    return decorator

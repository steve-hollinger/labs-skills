"""Valkey/Redis client utilities."""

from __future__ import annotations

import logging
from typing import Any

import redis

logger = logging.getLogger(__name__)


def get_client(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    decode_responses: bool = True,
    **kwargs: Any,
) -> redis.Redis:  # type: ignore[type-arg]
    """Create a Redis client with sensible defaults.

    Args:
        host: Redis host address.
        port: Redis port.
        db: Database number.
        decode_responses: Whether to decode responses to strings.
        **kwargs: Additional arguments passed to redis.Redis.

    Returns:
        Configured Redis client.

    Example:
        >>> client = get_client()
        >>> client.ping()
        True
    """
    client: redis.Redis[Any] = redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=decode_responses,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
        **kwargs,
    )

    return client


class ValkeyClient:
    """Wrapper around Redis client with additional utilities.

    Provides a higher-level interface for common operations and
    connection management.

    Example:
        >>> with ValkeyClient() as client:
        ...     client.set("key", "value", ttl=3600)
        ...     value = client.get("key")
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        max_connections: int = 10,
        default_ttl: int = 3600,
    ) -> None:
        """Initialize the Valkey client.

        Args:
            host: Redis host address.
            port: Redis port.
            db: Database number.
            max_connections: Maximum connections in pool.
            default_ttl: Default TTL for cache operations.
        """
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=max_connections,
            decode_responses=True,
        )
        self._client: redis.Redis[str] = redis.Redis(connection_pool=self._pool)
        self._default_ttl = default_ttl

    @property
    def client(self) -> redis.Redis[str]:
        """Get the underlying Redis client."""
        return self._client

    def ping(self) -> bool:
        """Check if the server is responsive."""
        try:
            return self._client.ping()
        except redis.ConnectionError:
            return False

    def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool | None:
        """Set a key with optional TTL and conditions.

        Args:
            key: Cache key.
            value: Value to store.
            ttl: Time-to-live in seconds (uses default if None).
            nx: Only set if key doesn't exist.
            xx: Only set if key exists.

        Returns:
            True if set successful, None if condition not met.
        """
        effective_ttl = ttl if ttl is not None else self._default_ttl
        return self._client.set(key, value, ex=effective_ttl, nx=nx, xx=xx)

    def get(self, key: str) -> str | None:
        """Get a value by key.

        Args:
            key: Cache key.

        Returns:
            Stored value or None if not found.
        """
        return self._client.get(key)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys.

        Args:
            *keys: Keys to delete.

        Returns:
            Number of keys deleted.
        """
        return self._client.delete(*keys)

    def exists(self, *keys: str) -> int:
        """Check if keys exist.

        Args:
            *keys: Keys to check.

        Returns:
            Number of keys that exist.
        """
        return self._client.exists(*keys)

    def ttl(self, key: str) -> int:
        """Get remaining TTL for a key.

        Args:
            key: Cache key.

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist.
        """
        return self._client.ttl(key)

    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on an existing key.

        Args:
            key: Cache key.
            ttl: Time-to-live in seconds.

        Returns:
            True if TTL was set.
        """
        return self._client.expire(key, ttl)

    def pipeline(self) -> redis.client.Pipeline:  # type: ignore[type-arg]
        """Create a pipeline for batch operations.

        Returns:
            Redis pipeline.
        """
        return self._client.pipeline()

    def info(self, section: str | None = None) -> dict[str, Any]:
        """Get server information.

        Args:
            section: Specific section (memory, stats, etc.).

        Returns:
            Server information dictionary.
        """
        return self._client.info(section)  # type: ignore[return-value]

    def close(self) -> None:
        """Close the connection pool."""
        self._pool.disconnect()
        logger.info("Valkey connection pool closed")

    def __enter__(self) -> ValkeyClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

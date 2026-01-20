"""Solution 2: Secret Caching with TTL and Metrics.

This solution demonstrates an enhanced secret cache with per-secret TTL,
metrics tracking, and thread safety.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from botocore.exceptions import ClientError


@dataclass
class CacheMetrics:
    """Metrics for cache operations."""

    hits: int = 0
    misses: int = 0
    refreshes: int = 0
    errors: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "refreshes": self.refreshes,
            "errors": self.errors,
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.hits = 0
        self.misses = 0
        self.refreshes = 0
        self.errors = 0


@dataclass
class CacheEntry:
    """A cached secret entry."""

    value: Any
    expires_at: float
    ttl: int
    last_accessed: float = field(default_factory=time.time)


class EnhancedSecretCache:
    """Enhanced secret cache with per-secret TTL and metrics."""

    def __init__(self, client: Any, default_ttl: int = 300):
        """Initialize the cache.

        Args:
            client: boto3 secretsmanager client
            default_ttl: Default TTL in seconds for secrets (default 5 minutes)
        """
        self.client = client
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._ttl_config: dict[str, int] = {}
        self._metrics = CacheMetrics()
        self._lock = Lock()

    def configure(self, secret_name: str, ttl: int) -> None:
        """Configure TTL for a specific secret.

        Args:
            secret_name: The secret name
            ttl: TTL in seconds for this secret
        """
        with self._lock:
            self._ttl_config[secret_name] = ttl

    def get_ttl(self, secret_name: str) -> int:
        """Get the configured TTL for a secret.

        Args:
            secret_name: The secret name

        Returns:
            TTL in seconds
        """
        return self._ttl_config.get(secret_name, self.default_ttl)

    def get(self, secret_name: str, force_refresh: bool = False) -> Any:
        """Get a secret, using cache if valid.

        Args:
            secret_name: The secret to retrieve
            force_refresh: If True, bypass cache

        Returns:
            The secret value

        Raises:
            KeyError: If secret not found
        """
        now = time.time()

        # Check cache first (unless force refresh)
        if not force_refresh:
            with self._lock:
                if secret_name in self._cache:
                    entry = self._cache[secret_name]
                    if now < entry.expires_at:
                        self._metrics.hits += 1
                        entry.last_accessed = now
                        return entry.value

        # Cache miss or expired - fetch from Secrets Manager
        with self._lock:
            self._metrics.misses += 1

        try:
            value = self._fetch_secret(secret_name)

            if force_refresh:
                with self._lock:
                    self._metrics.refreshes += 1

        except ClientError as e:
            with self._lock:
                self._metrics.errors += 1

            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise KeyError(f"Secret not found: {secret_name}") from e
            raise

        # Cache the result
        ttl = self.get_ttl(secret_name)
        with self._lock:
            self._cache[secret_name] = CacheEntry(
                value=value,
                expires_at=now + ttl,
                ttl=ttl,
                last_accessed=now,
            )

        return value

    def _fetch_secret(self, secret_name: str) -> Any:
        """Fetch a secret from Secrets Manager.

        Args:
            secret_name: The secret to fetch

        Returns:
            The secret value (parsed JSON if applicable)
        """
        response = self.client.get_secret_value(SecretId=secret_name)

        secret_string = response.get("SecretString")
        if secret_string:
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError:
                return secret_string

        return response.get("SecretBinary")

    def get_metrics(self) -> dict[str, int]:
        """Get cache metrics.

        Returns:
            Dict with hits, misses, refreshes, errors
        """
        with self._lock:
            return self._metrics.to_dict()

    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        with self._lock:
            self._metrics.reset()

    def invalidate(self, secret_name: str | None = None) -> None:
        """Invalidate cache entries.

        Args:
            secret_name: Specific secret to invalidate, or None for all
        """
        with self._lock:
            if secret_name:
                self._cache.pop(secret_name, None)
            else:
                self._cache.clear()

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about cached entries.

        Returns:
            Dict with cache entry details (excluding values)
        """
        now = time.time()
        with self._lock:
            return {
                name: {
                    "ttl": entry.ttl,
                    "expires_in": max(0, int(entry.expires_at - now)),
                    "last_accessed": entry.last_accessed,
                }
                for name, entry in self._cache.items()
            }


def main() -> None:
    """Demonstrate the EnhancedSecretCache."""
    import os

    from secrets_manager import get_secrets_client

    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Solution 2: Enhanced Secret Cache")
    print("=" * 60)

    client = get_secrets_client(use_localstack=True)

    # Clean up and create test secrets
    for name in ["test/cache-1", "test/cache-2"]:
        try:
            client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
        except Exception:
            pass

    print("\n1. Creating test secrets...")
    client.create_secret(
        Name="test/cache-1",
        SecretString=json.dumps({"key": "value1"}),
    )
    client.create_secret(
        Name="test/cache-2",
        SecretString=json.dumps({"key": "value2"}),
    )

    # Create cache with different TTLs
    print("\n2. Creating cache with per-secret TTL...")
    cache = EnhancedSecretCache(client, default_ttl=300)
    cache.configure("test/cache-1", ttl=60)   # 1 minute
    cache.configure("test/cache-2", ttl=600)  # 10 minutes

    print(f"   test/cache-1 TTL: {cache.get_ttl('test/cache-1')}s")
    print(f"   test/cache-2 TTL: {cache.get_ttl('test/cache-2')}s")

    # Fetch secrets
    print("\n3. Fetching secrets (cache miss)...")
    value1 = cache.get("test/cache-1")
    value2 = cache.get("test/cache-2")
    print(f"   cache-1: {value1}")
    print(f"   cache-2: {value2}")

    metrics = cache.get_metrics()
    print(f"   Metrics: {metrics}")

    # Fetch again (cache hit)
    print("\n4. Fetching again (cache hit)...")
    cache.get("test/cache-1")
    cache.get("test/cache-2")
    cache.get("test/cache-1")

    metrics = cache.get_metrics()
    print(f"   Metrics: {metrics}")
    print(f"   Hit rate: {metrics['hits'] / (metrics['hits'] + metrics['misses']) * 100:.1f}%")

    # Show cache info
    print("\n5. Cache info:")
    for name, info in cache.get_cache_info().items():
        print(f"   {name}: expires in {info['expires_in']}s")

    # Force refresh
    print("\n6. Force refresh...")
    cache.get("test/cache-1", force_refresh=True)
    metrics = cache.get_metrics()
    print(f"   Refreshes: {metrics['refreshes']}")

    # Invalidate one secret
    print("\n7. Invalidating test/cache-1...")
    cache.invalidate("test/cache-1")
    print(f"   Cache info: {cache.get_cache_info()}")

    # Fetch invalidated secret (miss)
    cache.get("test/cache-1")
    metrics = cache.get_metrics()
    print(f"   Metrics after refetch: {metrics}")

    # Reset metrics
    print("\n8. Resetting metrics...")
    cache.reset_metrics()
    print(f"   Metrics: {cache.get_metrics()}")

    # Clean up
    print("\n9. Cleaning up...")
    for name in ["test/cache-1", "test/cache-2"]:
        try:
            client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("Solution 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

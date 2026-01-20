"""Example 4: Rate Limiting.

This example demonstrates implementing rate limiting with Valkey/Redis
using the sliding window algorithm.

Learning objectives:
- Implement sliding window rate limiting
- Use sorted sets for time-based tracking
- Handle different rate limit tiers
- Build a complete rate limiter class

Prerequisites:
- Valkey running on localhost:6379
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import NamedTuple

import redis


class RateLimitResult(NamedTuple):
    """Result of a rate limit check."""

    allowed: bool
    remaining: int
    reset_in: float  # seconds until window resets


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests: int  # Max requests
    window: int  # Window size in seconds
    name: str = "default"


class RateLimiter:
    """Sliding window rate limiter using sorted sets.

    Uses Redis sorted sets where:
    - Score = timestamp
    - Member = unique request ID

    Sliding window removes old entries and counts current window.
    """

    def __init__(
        self,
        client: redis.Redis[str],
        prefix: str = "ratelimit",
    ) -> None:
        """Initialize rate limiter.

        Args:
            client: Redis client.
            prefix: Key prefix for rate limit keys.
        """
        self._client = client
        self._prefix = prefix

    def _key(self, identifier: str, config_name: str) -> str:
        """Create rate limit key."""
        return f"{self._prefix}:{config_name}:{identifier}"

    def check(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> RateLimitResult:
        """Check if request is allowed and record it.

        Args:
            identifier: Unique identifier (user ID, IP, API key).
            config: Rate limit configuration.

        Returns:
            RateLimitResult with allowed status and metadata.
        """
        key = self._key(identifier, config.name)
        now = time.time()
        window_start = now - config.window

        # Use pipeline for atomic operations
        pipe = self._client.pipeline()

        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current entries
        pipe.zcard(key)

        # Get oldest entry timestamp for reset calculation
        pipe.zrange(key, 0, 0, withscores=True)

        results = pipe.execute()
        current_count = results[1]
        oldest_entries = results[2]

        # Calculate reset time
        if oldest_entries:
            oldest_ts = oldest_entries[0][1]
            reset_in = max(0, (oldest_ts + config.window) - now)
        else:
            reset_in = float(config.window)

        # Check if allowed
        if current_count >= config.requests:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_in=reset_in,
            )

        # Add current request
        request_id = f"{now}-{id(now)}"  # Unique ID
        pipe = self._client.pipeline()
        pipe.zadd(key, {request_id: now})
        pipe.expire(key, config.window + 1)  # Extra second for safety
        pipe.execute()

        return RateLimitResult(
            allowed=True,
            remaining=config.requests - current_count - 1,
            reset_in=reset_in,
        )

    def get_usage(
        self,
        identifier: str,
        config: RateLimitConfig,
    ) -> tuple[int, int]:
        """Get current usage without recording a request.

        Args:
            identifier: Unique identifier.
            config: Rate limit configuration.

        Returns:
            Tuple of (current_count, max_requests).
        """
        key = self._key(identifier, config.name)
        now = time.time()
        window_start = now - config.window

        # Remove old and count
        pipe = self._client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        results = pipe.execute()

        return results[1], config.requests

    def reset(self, identifier: str, config: RateLimitConfig) -> bool:
        """Reset rate limit for an identifier.

        Args:
            identifier: Unique identifier.
            config: Rate limit configuration.

        Returns:
            True if key was deleted.
        """
        key = self._key(identifier, config.name)
        return self._client.delete(key) > 0


class TieredRateLimiter:
    """Rate limiter with multiple tiers (e.g., free, pro, enterprise)."""

    def __init__(
        self,
        client: redis.Redis[str],
        tiers: dict[str, RateLimitConfig],
    ) -> None:
        """Initialize tiered rate limiter.

        Args:
            client: Redis client.
            tiers: Mapping of tier name to config.
        """
        self._limiter = RateLimiter(client)
        self._tiers = tiers

    def check(self, identifier: str, tier: str) -> RateLimitResult:
        """Check rate limit for a specific tier.

        Args:
            identifier: Unique identifier.
            tier: Tier name (must exist in tiers).

        Returns:
            RateLimitResult.

        Raises:
            KeyError: If tier doesn't exist.
        """
        config = self._tiers[tier]
        return self._limiter.check(identifier, config)


def main() -> None:
    print("=" * 60)
    print("Example 4: Rate Limiting")
    print("=" * 60)

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
        print("\nMake sure Valkey is running:")
        print("  cd ../../.. && make infra-up")
        return

    # Clean up
    for key in client.scan_iter(match="ratelimit:*"):
        client.delete(key)

    # Part 1: Basic Rate Limiting
    print("\n" + "-" * 40)
    print("PART 1: Basic Rate Limiting")
    print("-" * 40)

    limiter = RateLimiter(client)

    # 5 requests per 10 seconds
    config = RateLimitConfig(requests=5, window=10, name="api")

    print(f"\n  Config: {config.requests} requests per {config.window} seconds")
    print("\n  Making requests:")

    for i in range(7):
        result = limiter.check("user-123", config)
        status = "ALLOWED" if result.allowed else "BLOCKED"
        print(
            f"    Request {i+1}: {status} "
            f"(remaining: {result.remaining}, reset in: {result.reset_in:.1f}s)"
        )
        time.sleep(0.1)

    # Part 2: Rate Limit Recovery
    print("\n" + "-" * 40)
    print("PART 2: Rate Limit Recovery")
    print("-" * 40)

    # Reset for fresh start
    limiter.reset("user-456", config)

    # Use up the limit
    print("\n  Using up rate limit...")
    for _ in range(5):
        limiter.check("user-456", config)

    result = limiter.check("user-456", config)
    print(f"  After 5 requests: allowed={result.allowed}")

    # Wait for partial recovery (with shorter window for demo)
    short_config = RateLimitConfig(requests=5, window=3, name="short")
    limiter.reset("user-456", short_config)

    print("\n  Testing recovery with 3-second window:")
    for _ in range(5):
        limiter.check("user-456", short_config)

    result = limiter.check("user-456", short_config)
    print(f"  Immediately after limit: allowed={result.allowed}")

    print("  Waiting 3 seconds for window to slide...")
    time.sleep(3.5)

    result = limiter.check("user-456", short_config)
    print(f"  After waiting: allowed={result.allowed}, remaining={result.remaining}")

    # Part 3: Tiered Rate Limiting
    print("\n" + "-" * 40)
    print("PART 3: Tiered Rate Limiting")
    print("-" * 40)

    tiers = {
        "free": RateLimitConfig(requests=10, window=60, name="free"),
        "pro": RateLimitConfig(requests=100, window=60, name="pro"),
        "enterprise": RateLimitConfig(requests=1000, window=60, name="enterprise"),
    }

    tiered_limiter = TieredRateLimiter(client, tiers)

    print("\n  Rate limit tiers:")
    for name, config in tiers.items():
        print(f"    {name}: {config.requests} req/min")

    # Simulate different users
    print("\n  Simulating API requests:")

    users = [
        ("free-user", "free"),
        ("pro-user", "pro"),
        ("enterprise-user", "enterprise"),
    ]

    for user_id, tier in users:
        # Make 15 requests
        allowed = 0
        blocked = 0
        for _ in range(15):
            result = tiered_limiter.check(user_id, tier)
            if result.allowed:
                allowed += 1
            else:
                blocked += 1

        print(f"    {tier:12} user: {allowed} allowed, {blocked} blocked (of 15)")

    # Part 4: IP-Based Rate Limiting
    print("\n" + "-" * 40)
    print("PART 4: IP-Based Rate Limiting")
    print("-" * 40)

    ip_config = RateLimitConfig(requests=3, window=5, name="ip")

    print(f"\n  Config: {ip_config.requests} requests per {ip_config.window} seconds per IP")

    ips = ["192.168.1.1", "192.168.1.2", "192.168.1.1"]
    print("\n  Requests from different IPs:")

    for ip in ips:
        result = limiter.check(ip, ip_config)
        status = "OK" if result.allowed else "BLOCKED"
        print(f"    {ip}: {status} (remaining: {result.remaining})")

    # Same IP exhausts its limit
    print("\n  Multiple requests from 192.168.1.1:")
    for i in range(4):
        result = limiter.check("192.168.1.1", ip_config)
        status = "OK" if result.allowed else "BLOCKED"
        print(f"    Request {i+1}: {status}")

    # Part 5: Check Usage Without Recording
    print("\n" + "-" * 40)
    print("PART 5: Usage Monitoring")
    print("-" * 40)

    # Reset and make some requests
    limiter.reset("monitor-user", config)
    for _ in range(3):
        limiter.check("monitor-user", config)

    # Check usage without incrementing
    current, maximum = limiter.get_usage("monitor-user", config)
    print(f"\n  Current usage: {current}/{maximum}")
    print("  (Checking usage doesn't count as a request)")

    # Verify by checking again
    current2, _ = limiter.get_usage("monitor-user", config)
    print(f"  Still at: {current2}/{maximum}")

    # Cleanup
    print("\n" + "-" * 40)
    print("Cleanup")
    print("-" * 40)
    deleted = 0
    for key in client.scan_iter(match="ratelimit:*"):
        client.delete(key)
        deleted += 1
    print(f"  Deleted {deleted} keys")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""Example 3: Rate Limiting and Key Rotation.

This example demonstrates:
- Tiered rate limiting
- Key rotation with grace periods
- Monitoring and metrics

Run with: make example-3
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any

from api_key_auth import (
    KeyStore,
    RateLimitConfig,
    SlidingWindowRateLimiter,
    generate_api_key,
)
from api_key_auth.rate_limiter import TieredRateLimiter, TokenBucketRateLimiter
from api_key_auth.storage import KeyTier


def demo_sliding_window() -> None:
    """Demonstrate sliding window rate limiter."""
    print("\n1. Sliding Window Rate Limiter")
    print("-" * 40)

    config = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        requests_per_day=100,
    )
    limiter = SlidingWindowRateLimiter(config)

    key_id = "test_key_1"

    print(f"Limits: {config.requests_per_minute}/min, {config.requests_per_hour}/hr")
    print("\nMaking requests...")

    for i in range(8):
        result = limiter.check(key_id)
        status = "Allowed" if result.allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}, Remaining: {result.remaining}")
        if not result.allowed:
            print(f"    Retry after: {result.retry_after:.1f}s")
            print(f"    Exceeded: {result.info.get('exceeded_window')}")
            break

    # Show current status
    print("\nCurrent status:")
    status = limiter.get_status(key_id)
    for window, info in status.items():
        print(f"  {window}: {info['used']}/{info['limit']} used, {info['remaining']} remaining")


def demo_token_bucket() -> None:
    """Demonstrate token bucket rate limiter."""
    print("\n2. Token Bucket Rate Limiter")
    print("-" * 40)

    # 1 request per second, burst of 5
    limiter = TokenBucketRateLimiter(rate=1.0, capacity=5)
    key_id = "test_key_2"

    print("Token bucket: 1 req/sec, capacity 5")
    print("\nBurst test (rapid requests)...")

    for i in range(7):
        result = limiter.check(key_id)
        status = "Allowed" if result.allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}, Tokens remaining: {result.remaining}")
        if not result.allowed:
            print(f"    Next token in: {result.retry_after:.2f}s")

    print("\nWaiting 2 seconds for tokens to refill...")
    time.sleep(2)

    for i in range(3):
        result = limiter.check(key_id)
        status = "Allowed" if result.allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}, Tokens: {result.remaining}")


def demo_tiered_limiting() -> None:
    """Demonstrate tiered rate limiting."""
    print("\n3. Tiered Rate Limiting")
    print("-" * 40)

    limiter = TieredRateLimiter()

    print("Tier configurations:")
    for tier in ["free", "basic", "pro", "enterprise"]:
        config = limiter.get_tier_config(tier)
        if config:
            print(f"  {tier:12}: {config.requests_per_minute}/min, "
                  f"{config.requests_per_hour}/hr, {config.requests_per_day}/day")

    # Simulate different tier users
    print("\nSimulating requests for different tiers...")

    users = [
        ("free_user", "free"),
        ("basic_user", "basic"),
        ("pro_user", "pro"),
    ]

    for user_id, tier in users:
        print(f"\n  {tier.upper()} tier ({user_id}):")
        for i in range(12):
            result = limiter.check(user_id, tier)
            if not result.allowed:
                print(f"    Blocked after {i} requests")
                break
        else:
            print(f"    12 requests allowed")


def demo_key_rotation() -> None:
    """Demonstrate key rotation with grace period."""
    print("\n4. Key Rotation with Grace Period")
    print("-" * 40)

    class RotatingKeyStore:
        """Key store with rotation support."""

        def __init__(self, grace_period: timedelta = timedelta(days=7)):
            self.store = KeyStore()
            self.grace_period = grace_period
            self._rotations: dict[str, dict[str, Any]] = {}

        def create_key(self, name: str, **kwargs) -> tuple[str, Any]:
            """Create a new key."""
            key = generate_api_key("sk_live")
            info = self.store.store(key, name, **kwargs)
            return key, info

        def rotate_key(self, old_key: str, name: str) -> tuple[str, Any, datetime]:
            """Rotate a key, keeping old one valid during grace period."""
            from api_key_auth.storage import hash_key

            # Verify old key
            old_info = self.store.get_by_key(old_key)
            if not old_info:
                raise ValueError("Old key not found")

            # Create new key
            new_key = generate_api_key("sk_live")
            new_info = self.store.store(
                new_key, name,
                owner_id=old_info.owner_id,
                tier=old_info.tier,
                metadata=old_info.metadata,
            )

            # Record rotation
            grace_end = datetime.utcnow() + self.grace_period
            old_hash = hash_key(old_key)
            new_hash = hash_key(new_key)

            self._rotations[old_hash] = {
                "new_hash": new_hash,
                "grace_end": grace_end,
            }

            return new_key, new_info, grace_end

        def validate(self, key: str) -> Any:
            """Validate a key, checking rotations."""
            from api_key_auth.storage import hash_key

            # Direct validation
            info = self.store.get_by_key(key)
            if info and info.is_active:
                return info

            # Check if rotated key in grace period
            key_hash = hash_key(key)
            if key_hash in self._rotations:
                rotation = self._rotations[key_hash]
                if datetime.utcnow() < rotation["grace_end"]:
                    # Return info for new key
                    for stored_info in self.store.list_keys():
                        if stored_info.key_hash == rotation["new_hash"]:
                            return stored_info

            return None

    # Demo rotation
    store = RotatingKeyStore(grace_period=timedelta(seconds=5))

    # Create original key
    old_key, old_info = store.create_key("My API Key", owner_id="user_123")
    print(f"Original key: {old_key[:30]}...")

    # Validate old key
    info = store.validate(old_key)
    print(f"Old key valid: {info is not None}")

    # Rotate key
    new_key, new_info, grace_end = store.rotate_key(old_key, "My API Key (rotated)")
    print(f"\nRotated to: {new_key[:30]}...")
    print(f"Grace period ends: {grace_end}")

    # Both keys should work during grace period
    print("\nDuring grace period:")
    print(f"  Old key valid: {store.validate(old_key) is not None}")
    print(f"  New key valid: {store.validate(new_key) is not None}")

    # Wait for grace period to end
    print("\nWaiting 6 seconds for grace period to end...")
    time.sleep(6)

    print("\nAfter grace period:")
    print(f"  Old key valid: {store.validate(old_key) is not None}")
    print(f"  New key valid: {store.validate(new_key) is not None}")


def demo_metrics() -> None:
    """Demonstrate rate limit metrics."""
    print("\n5. Rate Limit Metrics and Monitoring")
    print("-" * 40)

    config = RateLimitConfig(
        requests_per_minute=100,
        requests_per_hour=1000,
        requests_per_day=10000,
    )
    limiter = SlidingWindowRateLimiter(config)

    # Simulate some traffic
    key_ids = ["user_1", "user_2", "user_3"]

    for _ in range(50):
        for key_id in key_ids:
            limiter.check(key_id)

    # Collect metrics
    print("Current usage by user:")
    for key_id in key_ids:
        status = limiter.get_status(key_id)
        minute_used = status["minute"]["used"]
        hour_used = status["hour"]["used"]
        print(f"  {key_id}: {minute_used}/min, {hour_used}/hr")

    # Calculate totals
    total_minute = sum(limiter.get_status(k)["minute"]["used"] for k in key_ids)
    total_hour = sum(limiter.get_status(k)["hour"]["used"] for k in key_ids)

    print(f"\nTotal requests: {total_minute} in last minute, {total_hour} in last hour")

    # Alert simulation
    print("\nAlert thresholds:")
    for key_id in key_ids:
        status = limiter.get_status(key_id)
        minute_pct = status["minute"]["used"] / status["minute"]["limit"] * 100
        if minute_pct > 80:
            print(f"  WARNING: {key_id} at {minute_pct:.0f}% of minute limit")


def main() -> None:
    """Demonstrate rate limiting and key rotation."""
    print("=" * 60)
    print("Example 3: Rate Limiting and Key Rotation")
    print("=" * 60)

    demo_sliding_window()
    demo_token_bucket()
    demo_tiered_limiting()
    demo_key_rotation()
    demo_metrics()

    print("\n" + "=" * 60)
    print("Example 3 Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Sliding window: Good for strict limits, more memory")
    print("- Token bucket: Better for burst traffic, smoother")
    print("- Tiered limits: Different limits per customer tier")
    print("- Key rotation: Grace period prevents breaking changes")


if __name__ == "__main__":
    main()

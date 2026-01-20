"""Rate limiting utilities for API key authentication.

This module provides rate limiting functionality to prevent API abuse.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: int | None = None
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int | None = None  # Allow burst up to this many


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_at: float  # Unix timestamp
    retry_after: float | None = None  # Seconds until retry allowed
    info: dict[str, Any] = field(default_factory=dict)


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def check(self, key: str) -> RateLimitResult:
        """Check if a request is allowed.

        Args:
            key: The identifier to rate limit (e.g., API key ID)

        Returns:
            RateLimitResult
        """
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset the rate limit for a key.

        Args:
            key: The identifier to reset
        """
        pass


class SlidingWindowRateLimiter(RateLimiter):
    """Rate limiter using sliding window algorithm.

    This implementation maintains a list of request timestamps and
    counts requests within each time window.
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize the rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> RateLimitResult:
        """Check if a request is allowed.

        Args:
            key: The identifier to rate limit

        Returns:
            RateLimitResult with allow/deny decision
        """
        now = time.time()
        timestamps = self._requests[key]

        # Define time windows
        windows = {
            "minute": (60, self.config.requests_per_minute),
            "hour": (3600, self.config.requests_per_hour),
            "day": (86400, self.config.requests_per_day),
        }

        if self.config.requests_per_second:
            windows["second"] = (1, self.config.requests_per_second)

        # Remove old timestamps (older than longest window)
        max_window = max(w[0] for w in windows.values())
        cutoff = now - max_window
        timestamps = [t for t in timestamps if t > cutoff]
        self._requests[key] = timestamps

        # Count requests in each window
        window_counts: dict[str, dict[str, int]] = {}
        for name, (duration, limit) in windows.items():
            window_start = now - duration
            count = sum(1 for t in timestamps if t > window_start)
            window_counts[name] = {"count": count, "limit": limit}

        # Check if any limit exceeded
        for name, (duration, limit) in windows.items():
            count = window_counts[name]["count"]
            if count >= limit:
                # Find when the oldest request in this window will expire
                window_start = now - duration
                oldest_in_window = min(
                    (t for t in timestamps if t > window_start),
                    default=now
                )
                retry_after = oldest_in_window + duration - now

                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_at=oldest_in_window + duration,
                    retry_after=max(0, retry_after),
                    info={
                        "exceeded_window": name,
                        "window_counts": window_counts,
                    },
                )

        # Request allowed - record it
        timestamps.append(now)

        # Return info about the most restrictive window (usually minute)
        minute_count = window_counts["minute"]["count"]
        minute_limit = self.config.requests_per_minute

        return RateLimitResult(
            allowed=True,
            limit=minute_limit,
            remaining=minute_limit - minute_count - 1,
            reset_at=now + 60,
            info={"window_counts": window_counts},
        )

    def reset(self, key: str) -> None:
        """Reset rate limit for a key.

        Args:
            key: The identifier to reset
        """
        self._requests[key] = []

    def get_status(self, key: str) -> dict[str, dict[str, int]]:
        """Get current rate limit status for a key.

        Args:
            key: The identifier

        Returns:
            Dict with window counts and limits
        """
        now = time.time()
        timestamps = self._requests.get(key, [])

        windows = {
            "minute": (60, self.config.requests_per_minute),
            "hour": (3600, self.config.requests_per_hour),
            "day": (86400, self.config.requests_per_day),
        }

        result = {}
        for name, (duration, limit) in windows.items():
            window_start = now - duration
            count = sum(1 for t in timestamps if t > window_start)
            result[name] = {
                "used": count,
                "limit": limit,
                "remaining": max(0, limit - count),
            }

        return result


class TokenBucketRateLimiter(RateLimiter):
    """Rate limiter using token bucket algorithm.

    Better for handling burst traffic while maintaining average rate.
    """

    def __init__(
        self,
        rate: float,  # Tokens per second
        capacity: int,  # Maximum bucket size
    ):
        """Initialize the token bucket.

        Args:
            rate: Token refill rate per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last_update)

    def check(self, key: str) -> RateLimitResult:
        """Check if a request is allowed.

        Args:
            key: The identifier

        Returns:
            RateLimitResult
        """
        now = time.time()

        # Get or initialize bucket
        if key in self._buckets:
            tokens, last_update = self._buckets[key]
            # Add tokens based on time passed
            elapsed = now - last_update
            tokens = min(self.capacity, tokens + elapsed * self.rate)
        else:
            tokens = float(self.capacity)
            last_update = now

        # Check if we have a token
        if tokens >= 1:
            tokens -= 1
            self._buckets[key] = (tokens, now)
            return RateLimitResult(
                allowed=True,
                limit=self.capacity,
                remaining=int(tokens),
                reset_at=now + (self.capacity - tokens) / self.rate,
            )
        else:
            # Calculate when next token will be available
            retry_after = (1 - tokens) / self.rate
            self._buckets[key] = (tokens, now)
            return RateLimitResult(
                allowed=False,
                limit=self.capacity,
                remaining=0,
                reset_at=now + retry_after,
                retry_after=retry_after,
            )

    def reset(self, key: str) -> None:
        """Reset the bucket for a key.

        Args:
            key: The identifier
        """
        if key in self._buckets:
            del self._buckets[key]


class TieredRateLimiter:
    """Rate limiter with different limits per tier."""

    # Default tier configurations
    DEFAULT_TIERS = {
        "free": RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=1000,
        ),
        "basic": RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
        ),
        "pro": RateLimitConfig(
            requests_per_minute=300,
            requests_per_hour=5000,
            requests_per_day=50000,
        ),
        "enterprise": RateLimitConfig(
            requests_per_minute=1000,
            requests_per_hour=20000,
            requests_per_day=200000,
        ),
    }

    def __init__(
        self,
        tier_configs: dict[str, RateLimitConfig] | None = None,
    ):
        """Initialize the tiered rate limiter.

        Args:
            tier_configs: Custom tier configurations
        """
        configs = tier_configs or self.DEFAULT_TIERS
        self._limiters: dict[str, SlidingWindowRateLimiter] = {
            tier: SlidingWindowRateLimiter(config)
            for tier, config in configs.items()
        }

    def check(self, key: str, tier: str) -> RateLimitResult:
        """Check rate limit for a key based on its tier.

        Args:
            key: The identifier
            tier: The tier name

        Returns:
            RateLimitResult
        """
        limiter = self._limiters.get(tier)
        if not limiter:
            raise ValueError(f"Unknown tier: {tier}")
        result = limiter.check(key)
        result.info["tier"] = tier
        return result

    def reset(self, key: str, tier: str) -> None:
        """Reset rate limit for a key in a tier.

        Args:
            key: The identifier
            tier: The tier name
        """
        limiter = self._limiters.get(tier)
        if limiter:
            limiter.reset(key)

    def get_tier_config(self, tier: str) -> RateLimitConfig | None:
        """Get the configuration for a tier.

        Args:
            tier: The tier name

        Returns:
            RateLimitConfig or None
        """
        limiter = self._limiters.get(tier)
        return limiter.config if limiter else None

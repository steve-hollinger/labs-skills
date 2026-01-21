# Common Patterns

## Overview

This document covers common patterns and best practices for API key authentication.

## Pattern 1: FastAPI Integration

### When to Use

When building a FastAPI application that needs API key authentication.

### Implementation

```python
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Annotated

# Support both header and query (header preferred)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


class APIKeyAuth:
    """FastAPI dependency for API key authentication."""

    def __init__(
        self,
        validator: KeyValidator,
        rate_limiter: SlidingWindowRateLimiter | None = None,
    ):
        self.validator = validator
        self.rate_limiter = rate_limiter

    async def __call__(
        self,
        api_key_header: str | None = Security(api_key_header),
        api_key_query: str | None = Security(api_key_query),
    ) -> StoredKey:
        """Validate the API key."""
        # Prefer header over query
        api_key = api_key_header or api_key_query

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Validate key
        result = self.validator.validate(api_key)

        if result.result == ValidationResult.INVALID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        if result.result == ValidationResult.REVOKED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has been revoked",
            )

        if result.result == ValidationResult.EXPIRED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired",
            )

        # Check rate limit
        if self.rate_limiter and result.key_info:
            allowed, info = self.rate_limiter.check(result.key_info.id)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["minute"]["limit"]),
                        "X-RateLimit-Remaining": str(
                            info["minute"]["limit"] - info["minute"]["used"]
                        ),
                        "Retry-After": str(int(info.get("retry_after", 60))),
                    },
                )

        return result.key_info


# Usage
app = FastAPI()
auth = APIKeyAuth(validator, rate_limiter)

@app.get("/protected")
async def protected_endpoint(
    key_info: Annotated[StoredKey, Depends(auth)]
):
    return {"message": f"Hello, {key_info.name}!"}
```

### Pitfalls to Avoid

- Don't forget WWW-Authenticate header
- Always prefer header over query parameter
- Include rate limit headers in responses

## Pattern 2: Key Rotation with Grace Period

### When to Use

When you need to rotate keys without breaking existing integrations.

### Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class KeyRotation:
    """Manages key rotation with grace period."""

    old_key_hash: str
    new_key_hash: str
    rotated_at: datetime
    grace_period_ends: datetime


class RotatingKeyStore(KeyStore):
    """Key store that supports rotation with grace periods."""

    def __init__(self, grace_period: timedelta = timedelta(days=7)):
        super().__init__()
        self.grace_period = grace_period
        self._rotations: dict[str, KeyRotation] = {}

    def rotate_key(self, old_key: str, new_key: str, name: str) -> tuple[StoredKey, str]:
        """Rotate a key, keeping old key valid during grace period.

        Args:
            old_key: The current active key
            new_key: The new key to use
            name: Name for the new key

        Returns:
            Tuple of (new_stored_key, grace_period_end)
        """
        # Verify old key exists
        old_key_info = self.verify(old_key)
        if not old_key_info:
            raise ValueError("Old key not found")

        # Store new key
        new_stored = self.store(new_key, name)

        # Record rotation
        now = datetime.utcnow()
        grace_end = now + self.grace_period

        rotation = KeyRotation(
            old_key_hash=old_key_info.key_hash,
            new_key_hash=new_stored.key_hash,
            rotated_at=now,
            grace_period_ends=grace_end,
        )
        self._rotations[old_key_info.key_hash] = rotation

        return new_stored, grace_end.isoformat()

    def verify(self, key: str) -> StoredKey | None:
        """Verify a key, checking rotations."""
        # First try normal verification
        key_info = super().verify(key)
        if key_info:
            return key_info

        # Check if this is an old rotated key in grace period
        key_hash = hash_key(key)
        if key_hash in self._rotations:
            rotation = self._rotations[key_hash]
            if datetime.utcnow() < rotation.grace_period_ends:
                # Return the new key's info
                return self._keys.get(rotation.new_key_hash)

        return None

    def cleanup_expired_rotations(self) -> int:
        """Remove expired rotation records."""
        now = datetime.utcnow()
        expired = [
            hash for hash, rotation in self._rotations.items()
            if rotation.grace_period_ends < now
        ]
        for hash in expired:
            del self._rotations[hash]
        return len(expired)
```

### Example

```python
store = RotatingKeyStore(grace_period=timedelta(days=7))

# Create initial key
old_key = generate_api_key("sk_live")
store.store(old_key, "My API")

# Later, rotate the key
new_key = generate_api_key("sk_live")
new_info, grace_end = store.rotate_key(old_key, new_key, "My API (rotated)")

print(f"New key created. Old key valid until {grace_end}")

# Both keys work during grace period
assert store.verify(old_key) is not None
assert store.verify(new_key) is not None
```

### Pitfalls to Avoid

- Don't make grace period too short (breaks integrations)
- Don't make it too long (security risk)
- Clean up expired rotations regularly

## Pattern 3: Tiered Rate Limiting

### When to Use

When different API key types should have different limits.

### Implementation

```python
from enum import Enum


class KeyTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_LIMITS = {
    KeyTier.FREE: RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=1000,
    ),
    KeyTier.BASIC: RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
    ),
    KeyTier.PRO: RateLimitConfig(
        requests_per_minute=300,
        requests_per_hour=5000,
        requests_per_day=50000,
    ),
    KeyTier.ENTERPRISE: RateLimitConfig(
        requests_per_minute=1000,
        requests_per_hour=20000,
        requests_per_day=200000,
    ),
}


class TieredRateLimiter:
    """Rate limiter with tier-based limits."""

    def __init__(self):
        self._limiters: dict[KeyTier, SlidingWindowRateLimiter] = {
            tier: SlidingWindowRateLimiter(config)
            for tier, config in TIER_LIMITS.items()
        }

    def check(self, key_id: str, tier: KeyTier) -> tuple[bool, dict]:
        """Check rate limit for a key based on its tier."""
        limiter = self._limiters[tier]
        return limiter.check(key_id)


# Store keys with tier information
@dataclass
class TieredStoredKey(StoredKey):
    tier: KeyTier = KeyTier.FREE


# In FastAPI dependency
async def check_rate_limit(
    key_info: TieredStoredKey,
    rate_limiter: TieredRateLimiter,
):
    allowed, info = rate_limiter.check(key_info.id, key_info.tier)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {key_info.tier.value} tier"
        )
    return info
```

### Pitfalls to Avoid

- Don't allow tier changes without re-validation
- Consider burst allowances for spiky traffic
- Log tier usage for capacity planning

## Anti-Patterns

### Anti-Pattern 1: Keys in Logs

```python
# Bad - logs full key
logger.info(f"Request with API key: {api_key}")

# Good - log only prefix
logger.info(f"Request with API key: {api_key[:8]}...")
```

### Anti-Pattern 2: Plain Text Storage

```python
# Bad - storing plain key
db.execute("INSERT INTO keys (key) VALUES (?)", [api_key])

# Good - hash before storing
key_hash = hash_key(api_key)
db.execute("INSERT INTO keys (key_hash) VALUES (?)", [key_hash])
```

### Anti-Pattern 3: Key in URL Path

```python
# Bad - key in URL (logged everywhere)
@app.get("/api/{api_key}/data")

# Good - key in header
@app.get("/api/data")  # X-API-Key header
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Simple API | Basic FastAPI Integration |
| Production with rotation | Key Rotation with Grace |
| Multi-tier pricing | Tiered Rate Limiting |
| High-security | All patterns combined |

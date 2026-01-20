# Core Concepts

## Overview

API key authentication provides a simple way to identify and authenticate API clients. This document covers the core concepts for secure API key implementation.

## Concept 1: API Key Generation

### What It Is

API key generation creates unique, cryptographically secure identifiers for API clients. A well-designed key includes:
- A prefix for identification
- A random cryptographic portion
- Sufficient entropy to prevent guessing

### Why It Matters

- **Uniqueness**: Each client needs a unique identifier
- **Security**: Keys must be unguessable
- **Identification**: Prefixes help identify key type and environment

### How It Works

```python
import secrets
import string

def generate_api_key(
    prefix: str = "sk",
    length: int = 32,
    include_checksum: bool = False,
) -> str:
    """Generate a secure API key.

    Args:
        prefix: Key prefix (e.g., "sk_live", "pk_test")
        length: Length of random portion
        include_checksum: Whether to add checksum for validation

    Returns:
        Generated API key
    """
    # Generate cryptographically secure random bytes
    random_part = secrets.token_urlsafe(length)

    key = f"{prefix}_{random_part}"

    if include_checksum:
        # Add simple checksum for format validation
        checksum = sum(ord(c) for c in key) % 97
        key = f"{key}_{checksum:02d}"

    return key


# Example keys
print(generate_api_key("sk_live"))   # sk_example_FAKE24CHARSTRING12sD7f
print(generate_api_key("pk_test"))   # pk_test_aB3cD4eF5gH6iJ7kL8mN9oP0qR1s
print(generate_api_key("sk", include_checksum=True))  # sk_abc123_42
```

## Concept 2: Key Storage

### What It Is

Secure storage of API keys requires hashing, similar to password storage. The original key is never stored - only a hash that can verify the key.

### Why It Matters

- **Breach Protection**: If database is compromised, keys remain safe
- **Compliance**: Many regulations require hashing sensitive data
- **Best Practice**: Industry standard for credential storage

### How It Works

```python
import hashlib
from dataclasses import dataclass
from datetime import datetime


def hash_key(key: str) -> str:
    """Hash an API key for storage.

    Uses SHA-256 for fast verification (unlike passwords,
    we don't need slow hashing since keys have high entropy).
    """
    return hashlib.sha256(key.encode()).hexdigest()


def get_key_prefix(key: str) -> str:
    """Extract prefix from key for display."""
    parts = key.split("_")
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1][:4]}..."
    return key[:8] + "..."


@dataclass
class StoredKey:
    """A stored API key record."""
    id: str
    key_hash: str
    key_prefix: str  # For display: "sk_example_FAKE..."
    name: str
    created_at: datetime
    expires_at: datetime | None
    revoked: bool = False
    last_used: datetime | None = None
    metadata: dict | None = None


class KeyStore:
    """In-memory key store (use database in production)."""

    def __init__(self):
        self._keys: dict[str, StoredKey] = {}  # hash -> StoredKey

    def store(self, key: str, name: str, **kwargs) -> StoredKey:
        """Store a new API key (hashed)."""
        key_hash = hash_key(key)
        key_prefix = get_key_prefix(key)

        stored = StoredKey(
            id=key_hash[:16],  # Use hash prefix as ID
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            created_at=datetime.utcnow(),
            **kwargs
        )

        self._keys[key_hash] = stored
        return stored

    def verify(self, key: str) -> StoredKey | None:
        """Verify a key and return its info."""
        key_hash = hash_key(key)
        return self._keys.get(key_hash)
```

## Concept 3: Key Validation

### What It Is

Key validation verifies that incoming API requests have valid, active keys. This typically happens in middleware before the request handler.

### Why It Matters

- **Security**: Reject unauthorized requests early
- **Performance**: Validate once per request
- **Flexibility**: Apply different rules per key type

### How It Works

```python
from enum import Enum
from dataclasses import dataclass


class ValidationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RATE_LIMITED = "rate_limited"


@dataclass
class ValidationResponse:
    """Result of key validation."""
    result: ValidationResult
    key_info: StoredKey | None = None
    message: str | None = None


class KeyValidator:
    """Validates API keys."""

    def __init__(self, store: KeyStore):
        self.store = store

    def validate(self, key: str | None) -> ValidationResponse:
        """Validate an API key.

        Args:
            key: The API key to validate

        Returns:
            ValidationResponse with result and details
        """
        if not key:
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message="API key is required"
            )

        # Verify key exists
        key_info = self.store.verify(key)
        if not key_info:
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message="Invalid API key"
            )

        # Check if revoked
        if key_info.revoked:
            return ValidationResponse(
                result=ValidationResult.REVOKED,
                key_info=key_info,
                message="API key has been revoked"
            )

        # Check expiration
        if key_info.expires_at:
            from datetime import datetime
            if datetime.utcnow() > key_info.expires_at:
                return ValidationResponse(
                    result=ValidationResult.EXPIRED,
                    key_info=key_info,
                    message="API key has expired"
                )

        return ValidationResponse(
            result=ValidationResult.VALID,
            key_info=key_info
        )
```

## Concept 4: Rate Limiting

### What It Is

Rate limiting restricts how many requests a key can make in a time period, preventing abuse and ensuring fair usage.

### Why It Matters

- **Protection**: Prevent abuse and DoS attacks
- **Fairness**: Ensure resources for all clients
- **Cost Control**: Limit resource consumption

### How It Works

```python
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000


class SlidingWindowRateLimiter:
    """Rate limiter using sliding window algorithm."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        # Store request timestamps per key
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key_id: str) -> tuple[bool, dict]:
        """Check if request is allowed.

        Args:
            key_id: The API key identifier

        Returns:
            Tuple of (allowed, info_dict)
        """
        now = time.time()
        timestamps = self._requests[key_id]

        # Remove old timestamps
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400

        # Keep only last 24 hours
        timestamps = [t for t in timestamps if t > day_ago]
        self._requests[key_id] = timestamps

        # Count requests in each window
        last_minute = sum(1 for t in timestamps if t > minute_ago)
        last_hour = sum(1 for t in timestamps if t > hour_ago)
        last_day = len(timestamps)

        info = {
            "minute": {"used": last_minute, "limit": self.config.requests_per_minute},
            "hour": {"used": last_hour, "limit": self.config.requests_per_hour},
            "day": {"used": last_day, "limit": self.config.requests_per_day},
        }

        # Check limits
        if last_minute >= self.config.requests_per_minute:
            info["retry_after"] = 60 - (now - timestamps[-self.config.requests_per_minute])
            return False, info

        if last_hour >= self.config.requests_per_hour:
            info["retry_after"] = 3600 - (now - timestamps[-self.config.requests_per_hour])
            return False, info

        if last_day >= self.config.requests_per_day:
            info["retry_after"] = 86400 - (now - timestamps[-self.config.requests_per_day])
            return False, info

        # Record this request
        timestamps.append(now)
        return True, info
```

## Summary

Key takeaways:

1. **Generate secure keys** with prefixes and sufficient entropy
2. **Hash keys** before storage (never store plain text)
3. **Validate thoroughly** (existence, revocation, expiration)
4. **Rate limit** to prevent abuse
5. **Log safely** (never log full keys)

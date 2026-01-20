# Common Patterns

## Overview

This document covers common caching patterns and best practices for building robust caching solutions with Valkey/Redis.

## Pattern 1: Cache-Aside (Lazy Loading)

### When to Use

Most common pattern. Use when:
- Read-heavy workloads
- Cache misses are acceptable
- Data can become slightly stale

### Implementation

```python
import json
import redis
from typing import TypeVar, Callable, Any

T = TypeVar('T')

class CacheAside:
    """Cache-aside pattern implementation."""

    def __init__(self, client: redis.Redis, default_ttl: int = 3600):
        self.client = client
        self.default_ttl = default_ttl

    def get_or_set(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        """Get from cache or fetch and cache."""
        # Try cache first
        cached = self.client.get(key)
        if cached is not None:
            return json.loads(cached)

        # Cache miss - fetch from source
        value = fetch_fn()

        # Cache the result
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(value)
        )

        return value

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry."""
        self.client.delete(key)

# Usage
cache = CacheAside(client)

user = cache.get_or_set(
    key=f'user:{user_id}',
    fetch_fn=lambda: database.get_user(user_id),
    ttl=3600
)
```

### Pitfalls to Avoid

- Cache stampede on popular keys
- Not handling fetch failures
- Caching error responses

## Pattern 2: Write-Through

### When to Use

Use when:
- Cache must always be consistent with database
- Writes are not too frequent
- Read-after-write consistency required

### Implementation

```python
class WriteThrough:
    """Write-through cache pattern."""

    def __init__(self, client: redis.Redis, database: Any):
        self.client = client
        self.database = database

    def write(self, key: str, value: dict, ttl: int = 3600) -> None:
        """Write to both cache and database."""
        # Write to database first
        self.database.save(key, value)

        # Then update cache
        self.client.setex(key, ttl, json.dumps(value))

    def read(self, key: str) -> dict | None:
        """Read from cache, fallback to database."""
        cached = self.client.get(key)
        if cached:
            return json.loads(cached)

        # Fallback to database
        value = self.database.get(key)
        if value:
            self.client.setex(key, 3600, json.dumps(value))
        return value
```

### Pitfalls to Avoid

- Database write succeeds but cache write fails
- Increased write latency
- Not handling partial failures

## Pattern 3: Cache Stampede Prevention

### When to Use

When a popular cache key expires and many requests try to rebuild it simultaneously.

### Implementation

```python
import time
import uuid

class StampedeProtectedCache:
    """Cache with stampede protection using locking."""

    def __init__(self, client: redis.Redis):
        self.client = client

    def get_or_set_with_lock(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl: int = 3600,
        lock_timeout: int = 10,
    ) -> T | None:
        """Get from cache or fetch with lock protection."""
        # Try cache first
        cached = self.client.get(key)
        if cached is not None:
            return json.loads(cached)

        # Try to acquire lock
        lock_key = f'lock:{key}'
        lock_id = str(uuid.uuid4())

        if self.client.set(lock_key, lock_id, nx=True, ex=lock_timeout):
            try:
                # Double-check cache (another process might have filled it)
                cached = self.client.get(key)
                if cached is not None:
                    return json.loads(cached)

                # Fetch and cache
                value = fetch_fn()
                self.client.setex(key, ttl, json.dumps(value))
                return value
            finally:
                # Release lock (only if we own it)
                self._release_lock(lock_key, lock_id)
        else:
            # Wait for lock holder to populate cache
            for _ in range(lock_timeout * 10):
                time.sleep(0.1)
                cached = self.client.get(key)
                if cached is not None:
                    return json.loads(cached)
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
        self.client.eval(script, 1, key, lock_id)
```

### Pitfalls to Avoid

- Lock timeout too short
- Not handling lock holder failures
- Deadlocks from nested locks

## Pattern 4: Sliding Window Rate Limiting

### When to Use

To limit the rate of operations (API calls, login attempts, etc.) with a sliding time window.

### Implementation

```python
import time

class RateLimiter:
    """Sliding window rate limiter using sorted sets."""

    def __init__(self, client: redis.Redis):
        self.client = client

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Check if request is allowed.

        Returns (allowed, remaining_requests).
        """
        now = time.time()
        window_start = now - window_seconds

        pipe = self.client.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current entries
        pipe.zcard(key)

        # Add current request (optimistically)
        pipe.zadd(key, {str(now): now})

        # Set TTL
        pipe.expire(key, window_seconds)

        results = pipe.execute()
        current_count = results[1]

        if current_count >= max_requests:
            # Remove the optimistically added entry
            self.client.zrem(key, str(now))
            return False, 0

        return True, max_requests - current_count - 1

# Usage
limiter = RateLimiter(client)

# 100 requests per minute
allowed, remaining = limiter.is_allowed(
    key=f'ratelimit:user:{user_id}',
    max_requests=100,
    window_seconds=60
)

if not allowed:
    raise TooManyRequestsError("Rate limit exceeded")
```

### Pitfalls to Avoid

- Not cleaning up old entries
- Race conditions without pipeline
- Key collision between users

## Pattern 5: Session Management

### When to Use

For storing user sessions with automatic expiration.

### Implementation

```python
import secrets
from datetime import datetime
from pydantic import BaseModel

class Session(BaseModel):
    """Session data model."""
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    data: dict = {}

class SessionStore:
    """Redis-backed session store."""

    def __init__(
        self,
        client: redis.Redis,
        session_ttl: int = 3600,  # 1 hour
        prefix: str = 'session:'
    ):
        self.client = client
        self.session_ttl = session_ttl
        self.prefix = prefix

    def create(self, user_id: str, data: dict = {}) -> Session:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()

        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_accessed=now,
            data=data
        )

        key = f'{self.prefix}{session_id}'
        self.client.setex(
            key,
            self.session_ttl,
            session.model_dump_json()
        )

        return session

    def get(self, session_id: str) -> Session | None:
        """Get session and refresh TTL."""
        key = f'{self.prefix}{session_id}'
        data = self.client.get(key)

        if data is None:
            return None

        session = Session.model_validate_json(data)

        # Update last accessed and refresh TTL
        session.last_accessed = datetime.utcnow()
        self.client.setex(key, self.session_ttl, session.model_dump_json())

        return session

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        key = f'{self.prefix}{session_id}'
        return self.client.delete(key) > 0

    def update_data(self, session_id: str, data: dict) -> Session | None:
        """Update session data."""
        session = self.get(session_id)
        if session is None:
            return None

        session.data.update(data)
        key = f'{self.prefix}{session_id}'
        self.client.setex(key, self.session_ttl, session.model_dump_json())

        return session
```

### Pitfalls to Avoid

- Predictable session IDs (use cryptographic random)
- Not refreshing TTL on access
- Storing sensitive data unencrypted

## Anti-Patterns

### Anti-Pattern 1: Using Cache as Primary Storage

Cache should be a secondary storage that can be rebuilt from source.

```python
# Bad: Only storing in cache
def save_user(user: dict):
    client.set(f'user:{user["id"]}', json.dumps(user))

# Good: Cache as secondary storage
def save_user(user: dict):
    database.save_user(user)  # Primary storage
    client.setex(f'user:{user["id"]}', 3600, json.dumps(user))
```

### Anti-Pattern 2: Unbounded Keys

Always set TTL to prevent memory issues.

```python
# Bad: No TTL
client.set('cache:result', data)

# Good: Always set TTL
client.setex('cache:result', 3600, data)
```

### Anti-Pattern 3: Cache Everything

Not everything benefits from caching.

```python
# Bad: Caching unique per-request data
def get_request_id():
    return cache.get_or_set(f'request:{uuid4()}', generate_id)

# Good: Cache frequently accessed, expensive data
def get_product_catalog():
    return cache.get_or_set('catalog:products', fetch_catalog)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Read-heavy, tolerance for stale data | Cache-Aside |
| Must be consistent with database | Write-Through |
| Popular keys, high concurrency | Stampede Prevention |
| API rate limiting | Sliding Window Rate Limiter |
| User authentication | Session Management |
| Real-time counters | Atomic INCR operations |
| Leaderboards | Sorted Sets |

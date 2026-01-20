# CLAUDE.md - Valkey/Redis Caching

This skill teaches caching patterns using Valkey (Redis-compatible) with Python's redis-py library.

## Key Concepts

- **Caching**: Storing frequently accessed data in fast memory storage
- **Data Structures**: Strings, hashes, lists, sets, sorted sets for different use cases
- **TTL Management**: Time-based expiration to control cache lifetime
- **Cache Patterns**: Cache-aside, write-through, write-behind strategies
- **Eviction Policies**: LRU, LFU, and other memory management strategies
- **Atomic Operations**: INCR, DECR, SETNX for thread-safe operations

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
valkey-redis/
├── src/valkey_redis/
│   ├── __init__.py
│   ├── client.py           # Client wrapper utilities
│   ├── cache.py            # Cache implementation patterns
│   ├── session.py          # Session management
│   └── examples/
│       ├── example_1.py    # Basic operations
│       ├── example_2.py    # Caching patterns
│       ├── example_3.py    # Session management
│       └── example_4.py    # Rate limiting
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Connection
```python
import redis

# Create client with connection pool (recommended)
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    decode_responses=True,  # Return strings instead of bytes
    max_connections=10
)
client = redis.Redis(connection_pool=pool)

# Test connection
client.ping()
```

### Pattern 2: Cache-Aside Pattern
```python
import json
from typing import TypeVar, Callable

T = TypeVar('T')

def cached(key: str, ttl: int, fetch_fn: Callable[[], T]) -> T:
    """Generic cache-aside implementation."""
    # Try cache first
    cached_value = client.get(key)
    if cached_value is not None:
        return json.loads(cached_value)

    # Cache miss - fetch from source
    value = fetch_fn()

    # Store in cache
    client.setex(key, ttl, json.dumps(value))

    return value

# Usage
user = cached(
    key=f'user:{user_id}',
    ttl=3600,
    fetch_fn=lambda: database.get_user(user_id)
)
```

### Pattern 3: Distributed Lock
```python
import time
import uuid

def acquire_lock(key: str, timeout: int = 10) -> str | None:
    """Acquire a distributed lock."""
    lock_id = str(uuid.uuid4())
    if client.set(f'lock:{key}', lock_id, nx=True, ex=timeout):
        return lock_id
    return None

def release_lock(key: str, lock_id: str) -> bool:
    """Release lock only if we own it."""
    script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    return client.eval(script, 1, f'lock:{key}', lock_id) == 1

# Usage with context manager
from contextlib import contextmanager

@contextmanager
def distributed_lock(key: str, timeout: int = 10):
    lock_id = acquire_lock(key, timeout)
    if lock_id is None:
        raise Exception("Could not acquire lock")
    try:
        yield
    finally:
        release_lock(key, lock_id)
```

## Common Mistakes

1. **Not setting TTL on cache entries**
   - Leads to unbounded memory growth
   - Always use setex() or set(..., ex=ttl)

2. **Storing non-serializable objects**
   - Valkey stores strings/bytes
   - Always JSON serialize complex objects

3. **Not handling connection errors**
   - Network issues can cause failures
   - Implement fallback to source data

4. **Cache stampede on expiration**
   - Many requests rebuild cache simultaneously
   - Use locking or probabilistic early expiration

5. **Not using pipelines for batch operations**
   - Each command is a round-trip
   - Use pipeline() for multiple operations

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md. Ensure Valkey is running via `make infra-up` from repo root.

### "When should I use hashes vs strings?"
- Use strings for simple values or already-serialized JSON
- Use hashes when you need to update individual fields
- Hashes are more memory-efficient for small objects

### "How do I handle cache invalidation?"
- Delete on update: `client.delete('key')`
- Tag-based invalidation with sets
- Publish invalidation events to channels

### "What's the difference between Valkey and Redis?"
Valkey is an open-source fork of Redis, fully compatible with Redis clients and protocols. Use the same redis-py library.

### "How do I prevent memory issues?"
- Set maxmemory in Valkey config
- Use appropriate eviction policy (allkeys-lru recommended)
- Always set TTL on cache entries
- Monitor with INFO memory

## Testing Notes

- Tests use pytest with markers
- Integration tests require running Valkey
- Use `pytest -k "test_name"` for specific tests
- Check coverage: `make coverage`
- Use fakeredis for unit tests without Valkey

## Dependencies

Key dependencies in pyproject.toml:
- redis: Official Redis/Valkey client for Python
- pydantic: Schema validation
- pytest: Testing framework

## Infrastructure Requirements

Valkey must be running. Start from repo root:
```bash
make infra-up
```

This starts:
- Valkey on localhost:6379
- No authentication (development only)

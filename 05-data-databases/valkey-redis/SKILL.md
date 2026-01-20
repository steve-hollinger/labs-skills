---
name: caching-with-valkey
description: This skill teaches caching patterns using Valkey (Redis-compatible) with Python's redis-py library. Use when implementing authentication or verifying tokens.
---

# Valkey Redis

## Quick Start
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Key Points
- Caching
- Data Structures
- TTL Management

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
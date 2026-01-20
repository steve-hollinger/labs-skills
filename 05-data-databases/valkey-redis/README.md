# Valkey/Redis Caching

Master caching patterns with Valkey (the open-source Redis fork) - a high-performance in-memory data store used for caching, session management, real-time analytics, and message queuing.

## Learning Objectives

After completing this skill, you will be able to:
- Understand caching fundamentals and when to use them
- Work with Valkey/Redis data structures (strings, hashes, lists, sets, sorted sets)
- Implement TTL management and eviction policies
- Build caching patterns (cache-aside, write-through, write-behind)
- Use Python redis-py for Valkey/Redis operations
- Design effective caching strategies for real applications

## Prerequisites

- Python 3.11+
- UV package manager
- Docker (for local Valkey via shared infrastructure)
- Basic understanding of key-value stores

## Quick Start

```bash
# Start shared infrastructure (includes Valkey)
cd ../../../
make infra-up
cd 05-data-databases/valkey-redis

# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Why Valkey?

Valkey is an open-source fork of Redis, fully compatible with Redis protocols and clients. It offers:

- **Speed**: Sub-millisecond latency for most operations
- **Versatility**: Multiple data structures beyond simple key-value
- **Persistence**: Optional durability with RDB/AOF
- **Open Source**: Community-driven development under Linux Foundation

```python
import redis

# Connect to Valkey (same as Redis client)
client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Simple caching
client.set('user:123', '{"name": "Alice"}', ex=3600)  # 1 hour TTL
user = client.get('user:123')
```

## Concepts

### Data Structures

Valkey supports multiple data structures beyond simple strings:

```python
# Strings - Simple key-value
client.set('session:abc', 'user-123')

# Hashes - Field-value maps (like objects)
client.hset('user:123', mapping={'name': 'Alice', 'email': 'alice@example.com'})

# Lists - Ordered collections (queues)
client.lpush('queue:tasks', 'task-1', 'task-2')

# Sets - Unique unordered collections
client.sadd('tags:post:1', 'python', 'caching', 'redis')

# Sorted Sets - Scored unique elements (leaderboards)
client.zadd('leaderboard', {'player1': 100, 'player2': 85})
```

### TTL Management

Control data expiration with Time-To-Live:

```python
# Set with expiration
client.setex('cache:page:home', 300, html_content)  # 5 minutes

# Set TTL on existing key
client.expire('user:session', 1800)  # 30 minutes

# Check remaining TTL
ttl = client.ttl('cache:page:home')

# Remove TTL (persist forever)
client.persist('important:key')
```

### Cache Patterns

The cache-aside pattern is most common:

```python
def get_user(user_id: str) -> dict:
    # Try cache first
    cached = client.get(f'user:{user_id}')
    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    user = database.get_user(user_id)

    # Store in cache
    client.setex(f'user:{user_id}', 3600, json.dumps(user))

    return user
```

## Examples

### Example 1: Basic Operations

Learn fundamental Valkey operations with different data types.

```bash
make example-1
```

### Example 2: Caching Patterns

Implement cache-aside, write-through, and cache invalidation patterns.

```bash
make example-2
```

### Example 3: Session Management

Build a session store with automatic expiration.

```bash
make example-3
```

### Example 4: Rate Limiting

Implement sliding window rate limiting with sorted sets.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Cache Manager - Implement a generic caching wrapper with TTL
2. **Exercise 2**: Create a Leaderboard System - Use sorted sets for game rankings
3. **Exercise 3**: Implement a Shopping Cart - Use hashes for cart storage with expiration

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Setting TTL

Always set TTL to prevent unbounded memory growth:

```python
# Wrong - no expiration, memory leak risk
client.set('cache:data', value)

# Correct - always set TTL
client.setex('cache:data', 3600, value)
```

### Cache Stampede

Multiple processes rebuilding cache simultaneously:

```python
# Wrong - cache stampede on expiration
if not client.exists('expensive:query'):
    result = expensive_database_query()
    client.set('expensive:query', result)

# Correct - use locking
lock_key = 'lock:expensive:query'
if client.set(lock_key, '1', nx=True, ex=10):  # Acquire lock
    try:
        result = expensive_database_query()
        client.setex('expensive:query', 3600, result)
    finally:
        client.delete(lock_key)  # Release lock
```

### Serialization Issues

Remember to serialize/deserialize complex types:

```python
# Wrong - stores string representation, not JSON
client.set('user', {'name': 'Alice'})  # Stores "{'name': 'Alice'}"

# Correct - serialize to JSON
import json
client.set('user', json.dumps({'name': 'Alice'}))
user = json.loads(client.get('user'))
```

## Infrastructure

This skill uses the shared Valkey infrastructure:

- **Host**: localhost
- **Port**: 6379
- **No authentication** (local development only)

Start infrastructure from repository root:
```bash
make infra-up
```

## Performance Tips

1. **Pipeline Commands**: Batch operations to reduce round trips
2. **Use Appropriate Types**: Hashes for objects, sorted sets for rankings
3. **Monitor Memory**: Use `INFO memory` to track usage
4. **Set Max Memory**: Configure `maxmemory` and eviction policy

## Further Reading

- [Valkey Documentation](https://valkey.io/docs/)
- [Redis Documentation](https://redis.io/documentation) (compatible)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- Related skills in this repository:
  - [Kafka Event Streaming](../kafka-event-streaming/) - Event-driven patterns
  - [DynamoDB Schema](../dynamodb-schema/) - Another data storage option

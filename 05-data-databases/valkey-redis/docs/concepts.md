# Core Concepts

## Overview

This document covers the fundamental concepts of caching with Valkey/Redis, including data structures, TTL management, and when to use caching effectively.

## Concept 1: What is Caching?

### What It Is

Caching is the practice of storing frequently accessed data in a fast-access location (typically in-memory) to reduce latency and load on primary data stores.

### Why It Matters

- **Performance**: Sub-millisecond access vs. milliseconds for database queries
- **Scalability**: Reduce load on databases during high traffic
- **Cost**: Fewer database connections and compute resources
- **User Experience**: Faster response times

### How It Works

```python
import redis
import json
from typing import Any

client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_user_profile(user_id: str) -> dict[str, Any]:
    """Get user profile with caching."""
    cache_key = f'user:profile:{user_id}'

    # Check cache first (fast path)
    cached = client.get(cache_key)
    if cached:
        print(f"Cache HIT for {user_id}")
        return json.loads(cached)

    # Cache miss - fetch from database (slow path)
    print(f"Cache MISS for {user_id}")
    profile = fetch_from_database(user_id)  # Simulated DB call

    # Store in cache for future requests
    client.setex(cache_key, 3600, json.dumps(profile))

    return profile
```

## Concept 2: Valkey/Redis Data Structures

### What It Is

Valkey provides multiple data structures beyond simple key-value strings, each optimized for different use cases.

### Why It Matters

- **Efficiency**: Use the right structure for your data pattern
- **Atomic Operations**: Built-in operations for each type
- **Memory Optimization**: Different structures have different memory characteristics
- **Simplicity**: No need for complex data modeling

### How It Works

#### Strings
The simplest type - stores text, numbers, or serialized data.

```python
# Basic string operations
client.set('name', 'Alice')
client.get('name')  # 'Alice'

# Numeric operations
client.set('counter', 0)
client.incr('counter')  # 1
client.incrby('counter', 10)  # 11

# With expiration
client.setex('session', 3600, 'data')  # Expires in 1 hour

# Conditional set
client.setnx('lock', '1')  # Set only if not exists
```

#### Hashes
Field-value maps, ideal for representing objects.

```python
# Store an object
client.hset('user:123', mapping={
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': '30'
})

# Get single field
name = client.hget('user:123', 'name')  # 'Alice'

# Get all fields
user = client.hgetall('user:123')  # {'name': 'Alice', ...}

# Update single field
client.hset('user:123', 'age', '31')

# Increment numeric field
client.hincrby('user:123', 'login_count', 1)
```

#### Lists
Ordered collections, perfect for queues and recent items.

```python
# Add to list (queue)
client.lpush('queue:tasks', 'task3', 'task2', 'task1')  # Left push
client.rpush('queue:tasks', 'task4')  # Right push

# Pop from queue
task = client.rpop('queue:tasks')  # 'task4' (FIFO with lpush/rpop)
task = client.lpop('queue:tasks')  # 'task1' (LIFO with lpush/lpop)

# Get range (recent items)
recent = client.lrange('recent:posts', 0, 9)  # Last 10 posts

# Trim list (keep only recent)
client.ltrim('recent:posts', 0, 99)  # Keep only 100 items
```

#### Sets
Unordered unique collections, great for tags and memberships.

```python
# Add members
client.sadd('tags:post:1', 'python', 'caching', 'redis')

# Check membership
is_tagged = client.sismember('tags:post:1', 'python')  # True

# Get all members
tags = client.smembers('tags:post:1')  # {'python', 'caching', 'redis'}

# Set operations
client.sadd('tags:post:2', 'python', 'databases')
common = client.sinter('tags:post:1', 'tags:post:2')  # {'python'}
all_tags = client.sunion('tags:post:1', 'tags:post:2')  # All unique tags
```

#### Sorted Sets
Scored unique members, perfect for leaderboards and time-series.

```python
# Add with scores
client.zadd('leaderboard', {
    'player1': 100,
    'player2': 85,
    'player3': 120
})

# Get top players
top = client.zrevrange('leaderboard', 0, 2, withscores=True)
# [('player3', 120.0), ('player1', 100.0), ('player2', 85.0)]

# Get player rank
rank = client.zrevrank('leaderboard', 'player1')  # 1 (0-indexed)

# Increment score
client.zincrby('leaderboard', 10, 'player2')  # New score: 95

# Range by score
players = client.zrangebyscore('leaderboard', 80, 100)
```

## Concept 3: TTL (Time-To-Live) Management

### What It Is

TTL specifies how long data should remain in the cache before automatic deletion. It's crucial for cache freshness and memory management.

### Why It Matters

- **Freshness**: Cached data doesn't become stale forever
- **Memory Management**: Automatic cleanup prevents unbounded growth
- **Invalidation**: Simple time-based invalidation strategy
- **Compliance**: Remove data after retention period

### How It Works

```python
# Set with TTL
client.setex('cache:page:home', 300, html_content)  # 5 minutes
client.set('cache:api:result', data, ex=60)  # 60 seconds

# Add TTL to existing key
client.expire('user:session', 1800)  # 30 minutes from now
client.expireat('event:ticket', 1704067200)  # Unix timestamp

# Check TTL
remaining = client.ttl('cache:page:home')  # Seconds remaining (-1 if no TTL)
remaining_ms = client.pttl('cache:page:home')  # Milliseconds

# Remove TTL (persist key)
client.persist('important:data')

# Set TTL only if key exists
client.expire('maybe:exists', 3600, xx=True)
```

## Concept 4: Eviction Policies

### What It Is

When Valkey reaches its memory limit, eviction policies determine which keys to remove to make room for new data.

### Why It Matters

- **Memory Bounds**: Prevent out-of-memory errors
- **Cache Efficiency**: Keep frequently used data
- **Predictability**: Understand what gets evicted

### How It Works

Common eviction policies:

1. **noeviction**: Return errors when memory limit reached
2. **allkeys-lru**: Evict least recently used keys (recommended for caching)
3. **allkeys-lfu**: Evict least frequently used keys
4. **volatile-lru**: Evict LRU among keys with TTL
5. **volatile-ttl**: Evict keys with shortest TTL

```python
# Check current memory usage
info = client.info('memory')
print(f"Used memory: {info['used_memory_human']}")
print(f"Peak memory: {info['used_memory_peak_human']}")

# Get eviction stats
stats = client.info('stats')
print(f"Evicted keys: {stats['evicted_keys']}")

# Configure maxmemory (in redis.conf or via CONFIG SET)
# maxmemory 256mb
# maxmemory-policy allkeys-lru
```

## Concept 5: Atomic Operations

### What It Is

Operations that complete entirely or not at all, ensuring data consistency in concurrent environments.

### Why It Matters

- **Race Conditions**: Prevent data corruption from concurrent access
- **Counters**: Safe increment/decrement operations
- **Locks**: Implement distributed locking
- **Transactions**: Group operations atomically

### How It Works

```python
# Atomic increment (thread-safe counter)
client.incr('page:views')
client.incrby('account:balance', 100)
client.incrbyfloat('metric:value', 0.5)

# Atomic set-if-not-exists (for locking)
acquired = client.setnx('lock:resource', 'owner-id')  # True if acquired
# Or with expiration
acquired = client.set('lock:resource', 'owner-id', nx=True, ex=10)

# Transactions with MULTI/EXEC
pipe = client.pipeline()
pipe.decrby('account:A', 100)
pipe.incrby('account:B', 100)
pipe.execute()  # Both or neither

# Watch for optimistic locking
with client.pipeline() as pipe:
    while True:
        try:
            pipe.watch('inventory:item:1')
            quantity = int(pipe.get('inventory:item:1') or 0)
            if quantity < 1:
                pipe.unwatch()
                raise Exception("Out of stock")
            pipe.multi()
            pipe.decrby('inventory:item:1', 1)
            pipe.execute()
            break
        except redis.WatchError:
            continue  # Retry if key changed
```

## Summary

Key takeaways:

1. **Caching** dramatically improves performance by reducing database load
2. **Data structures** provide optimized operations for different patterns
3. **TTL management** ensures cache freshness and controls memory
4. **Eviction policies** handle memory limits gracefully
5. **Atomic operations** ensure data consistency in concurrent systems

Choose the right data structure and TTL for your use case, and always plan for cache misses and eviction.

"""Example 1: Basic Operations with Valkey/Redis.

This example demonstrates fundamental Valkey operations with different
data structures.

Learning objectives:
- Connect to Valkey/Redis
- Work with strings, hashes, lists, sets, and sorted sets
- Understand TTL and expiration
- Use atomic operations

Prerequisites:
- Valkey running on localhost:6379
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import time

import redis


def main() -> None:
    print("=" * 60)
    print("Example 1: Basic Valkey/Redis Operations")
    print("=" * 60)

    # Connect to Valkey
    try:
        client: redis.Redis[str] = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )
        client.ping()
        print("\n[OK] Connected to Valkey")
    except redis.ConnectionError as e:
        print(f"\n[ERROR] Could not connect to Valkey: {e}")
        print("\nMake sure Valkey is running:")
        print("  cd ../../.. && make infra-up")
        return

    # Clean up any existing keys from previous runs
    for key in client.scan_iter(match="example1:*"):
        client.delete(key)

    # Part 1: Strings
    print("\n" + "-" * 40)
    print("PART 1: Strings")
    print("-" * 40)

    # Basic set/get
    client.set("example1:name", "Alice")
    name = client.get("example1:name")
    print(f"  Set and get string: {name}")

    # Set with expiration
    client.setex("example1:session", 10, "session-data")
    ttl = client.ttl("example1:session")
    print(f"  Set with TTL: session expires in {ttl} seconds")

    # Conditional set (only if not exists)
    result1 = client.setnx("example1:lock", "owner1")
    result2 = client.setnx("example1:lock", "owner2")  # Should fail
    print(f"  SETNX first attempt: {result1}, second: {result2}")

    # Atomic increment
    client.set("example1:counter", 0)
    for _ in range(5):
        client.incr("example1:counter")
    count = client.get("example1:counter")
    print(f"  Incremented counter to: {count}")

    # Part 2: Hashes
    print("\n" + "-" * 40)
    print("PART 2: Hashes (Objects)")
    print("-" * 40)

    # Store an object as hash
    user = {
        "name": "Bob",
        "email": "bob@example.com",
        "age": "30",
        "login_count": "0",
    }
    client.hset("example1:user:1", mapping=user)
    print(f"  Stored user hash with {len(user)} fields")

    # Get single field
    email = client.hget("example1:user:1", "email")
    print(f"  Get single field (email): {email}")

    # Get all fields
    user_data = client.hgetall("example1:user:1")
    print(f"  Get all fields: {user_data}")

    # Increment a field
    client.hincrby("example1:user:1", "login_count", 1)
    login_count = client.hget("example1:user:1", "login_count")
    print(f"  Incremented login_count to: {login_count}")

    # Part 3: Lists
    print("\n" + "-" * 40)
    print("PART 3: Lists (Queues)")
    print("-" * 40)

    # Create a task queue
    tasks = ["task-1", "task-2", "task-3"]
    for task in tasks:
        client.rpush("example1:queue", task)
    print(f"  Added {len(tasks)} tasks to queue")

    # Get queue length
    length = client.llen("example1:queue")
    print(f"  Queue length: {length}")

    # Pop from queue (FIFO with rpush/lpop)
    task = client.lpop("example1:queue")
    print(f"  Popped task: {task}")

    # Get remaining items
    remaining = client.lrange("example1:queue", 0, -1)
    print(f"  Remaining: {remaining}")

    # Part 4: Sets
    print("\n" + "-" * 40)
    print("PART 4: Sets (Unique Collections)")
    print("-" * 40)

    # Add tags to posts
    client.sadd("example1:tags:post1", "python", "caching", "redis")
    client.sadd("example1:tags:post2", "python", "databases", "postgresql")
    print("  Added tags to two posts")

    # Check membership
    is_python = client.sismember("example1:tags:post1", "python")
    is_java = client.sismember("example1:tags:post1", "java")
    print(f"  Post1 has 'python': {is_python}, has 'java': {is_java}")

    # Set operations
    common = client.sinter("example1:tags:post1", "example1:tags:post2")
    all_tags = client.sunion("example1:tags:post1", "example1:tags:post2")
    print(f"  Common tags: {common}")
    print(f"  All unique tags: {all_tags}")

    # Part 5: Sorted Sets
    print("\n" + "-" * 40)
    print("PART 5: Sorted Sets (Leaderboards)")
    print("-" * 40)

    # Create a leaderboard
    scores = {
        "player1": 100,
        "player2": 85,
        "player3": 120,
        "player4": 95,
    }
    client.zadd("example1:leaderboard", scores)
    print(f"  Created leaderboard with {len(scores)} players")

    # Get top 3 players
    top3 = client.zrevrange("example1:leaderboard", 0, 2, withscores=True)
    print("  Top 3 players:")
    for rank, (player, score) in enumerate(top3, 1):
        print(f"    {rank}. {player}: {int(score)} points")

    # Get player rank
    rank = client.zrevrank("example1:leaderboard", "player2")
    print(f"  player2's rank: {rank + 1 if rank is not None else 'N/A'}")

    # Update score
    client.zincrby("example1:leaderboard", 50, "player2")
    new_score = client.zscore("example1:leaderboard", "player2")
    print(f"  player2's new score: {int(new_score or 0)}")

    # Part 6: TTL Management
    print("\n" + "-" * 40)
    print("PART 6: TTL Management")
    print("-" * 40)

    # Set key with TTL
    client.setex("example1:temp", 5, "temporary data")
    print("  Set key with 5 second TTL")

    # Check TTL
    for i in range(3):
        ttl = client.ttl("example1:temp")
        exists = client.exists("example1:temp")
        print(f"  After {i}s: TTL={ttl}s, exists={bool(exists)}")
        time.sleep(1)

    # Add TTL to existing key
    client.set("example1:permanent", "data")
    print(f"  Key without TTL: TTL={client.ttl('example1:permanent')}")
    client.expire("example1:permanent", 3600)
    print(f"  After EXPIRE: TTL={client.ttl('example1:permanent')}")

    # Part 7: Pipelines
    print("\n" + "-" * 40)
    print("PART 7: Pipelines (Batch Operations)")
    print("-" * 40)

    # Without pipeline: multiple round trips
    start = time.time()
    for i in range(100):
        client.incr("example1:no_pipeline")
    no_pipe_time = time.time() - start

    # With pipeline: single round trip
    start = time.time()
    pipe = client.pipeline()
    for i in range(100):
        pipe.incr("example1:with_pipeline")
    pipe.execute()
    pipe_time = time.time() - start

    print(f"  100 operations without pipeline: {no_pipe_time*1000:.2f}ms")
    print(f"  100 operations with pipeline: {pipe_time*1000:.2f}ms")
    print(f"  Pipeline is {no_pipe_time/pipe_time:.1f}x faster")

    # Cleanup
    print("\n" + "-" * 40)
    print("Cleanup")
    print("-" * 40)
    deleted = 0
    for key in client.scan_iter(match="example1:*"):
        client.delete(key)
        deleted += 1
    print(f"  Deleted {deleted} example keys")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

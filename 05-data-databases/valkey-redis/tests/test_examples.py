"""Tests for Valkey/Redis Caching examples.

These tests verify the caching utilities work correctly.
Some tests use fakeredis for unit testing without Valkey.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

# Try to import fakeredis for unit tests
try:
    import fakeredis

    HAS_FAKEREDIS = True
except ImportError:
    HAS_FAKEREDIS = False

from valkey_redis.cache import CacheManager


@pytest.fixture
def fake_client() -> Any:
    """Create a fake Redis client for testing."""
    if not HAS_FAKEREDIS:
        pytest.skip("fakeredis not installed")
    return fakeredis.FakeRedis(decode_responses=True)


class TestCacheManager:
    """Tests for CacheManager class."""

    def test_set_and_get(self, fake_client: Any) -> None:
        """Test basic set and get operations."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="test")

        cache.set("key1", {"value": "test"})
        result = cache.get("key1")

        assert result == {"value": "test"}

    def test_get_nonexistent(self, fake_client: Any) -> None:
        """Test getting a nonexistent key."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="test")

        result = cache.get("nonexistent")

        assert result is None

    def test_delete(self, fake_client: Any) -> None:
        """Test deleting a key."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="test")

        cache.set("to_delete", "value")
        assert cache.get("to_delete") == "value"

        deleted = cache.delete("to_delete")
        assert deleted is True

        assert cache.get("to_delete") is None

    def test_get_or_set_miss(self, fake_client: Any) -> None:
        """Test get_or_set on cache miss."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="test")
        fetch_called = False

        def fetch_fn() -> dict[str, str]:
            nonlocal fetch_called
            fetch_called = True
            return {"fetched": True}

        result = cache.get_or_set("missing_key", fetch_fn)

        assert result == {"fetched": True}
        assert fetch_called is True

    def test_get_or_set_hit(self, fake_client: Any) -> None:
        """Test get_or_set on cache hit."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="test")
        fetch_called = False

        cache.set("existing_key", {"cached": True})

        def fetch_fn() -> dict[str, bool]:
            nonlocal fetch_called
            fetch_called = True
            return {"fetched": True}

        result = cache.get_or_set("existing_key", fetch_fn)

        assert result == {"cached": True}
        assert fetch_called is False

    def test_key_prefix(self, fake_client: Any) -> None:
        """Test key prefix is applied correctly."""
        cache = CacheManager(fake_client, default_ttl=3600, key_prefix="myapp")

        cache.set("test", "value")

        # Check the actual key in Redis
        assert fake_client.get("myapp:test") == json.dumps("value")


class TestDataStructures:
    """Tests for Redis data structure patterns."""

    def test_hash_operations(self, fake_client: Any) -> None:
        """Test hash operations for object storage."""
        fake_client.hset(
            "user:1",
            mapping={"name": "Alice", "email": "alice@example.com"},
        )

        name = fake_client.hget("user:1", "name")
        assert name == "Alice"

        all_fields = fake_client.hgetall("user:1")
        assert all_fields == {"name": "Alice", "email": "alice@example.com"}

    def test_list_operations(self, fake_client: Any) -> None:
        """Test list operations for queues."""
        fake_client.rpush("queue", "task1", "task2", "task3")

        length = fake_client.llen("queue")
        assert length == 3

        task = fake_client.lpop("queue")
        assert task == "task1"

        remaining = fake_client.lrange("queue", 0, -1)
        assert remaining == ["task2", "task3"]

    def test_set_operations(self, fake_client: Any) -> None:
        """Test set operations for unique collections."""
        fake_client.sadd("tags:1", "python", "redis", "caching")
        fake_client.sadd("tags:2", "python", "databases")

        is_member = fake_client.sismember("tags:1", "python")
        assert is_member is True

        common = fake_client.sinter("tags:1", "tags:2")
        assert common == {"python"}

    def test_sorted_set_operations(self, fake_client: Any) -> None:
        """Test sorted set operations for leaderboards."""
        fake_client.zadd("scores", {"player1": 100, "player2": 85, "player3": 120})

        top = fake_client.zrevrange("scores", 0, 1, withscores=True)
        assert top[0] == ("player3", 120.0)

        rank = fake_client.zrevrank("scores", "player1")
        assert rank == 1  # 0-indexed, so second place

    def test_atomic_increment(self, fake_client: Any) -> None:
        """Test atomic increment operations."""
        fake_client.set("counter", "0")

        for _ in range(10):
            fake_client.incr("counter")

        value = int(fake_client.get("counter") or 0)
        assert value == 10


class TestPatterns:
    """Tests for caching patterns."""

    def test_rate_limiting_pattern(self, fake_client: Any) -> None:
        """Test sliding window rate limiting pattern."""
        import time

        key = "ratelimit:user:1"
        max_requests = 3
        window = 10  # seconds

        # Simulate requests
        now = time.time()
        for i in range(3):
            fake_client.zadd(key, {f"req-{i}": now + i * 0.1})

        # Count requests in window
        count = fake_client.zcard(key)
        assert count == 3

        # Should be at limit
        assert count >= max_requests

    def test_session_pattern(self, fake_client: Any) -> None:
        """Test session storage pattern."""
        session_id = "abc123"
        key = f"session:{session_id}"

        # Create session
        session_data = {
            "user_id": "user-1",
            "created_at": "2024-01-01T00:00:00",
            "data": json.dumps({"theme": "dark"}),
        }
        fake_client.hset(key, mapping=session_data)
        fake_client.expire(key, 3600)

        # Retrieve session
        session = fake_client.hgetall(key)
        assert session["user_id"] == "user-1"

        # Check TTL
        ttl = fake_client.ttl(key)
        assert ttl > 0


# Integration tests would go here, marked with pytest.mark.integration
@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring running Valkey."""

    def test_real_connection(self) -> None:
        """Test connection to real Valkey instance."""
        pytest.skip("Requires running Valkey instance")

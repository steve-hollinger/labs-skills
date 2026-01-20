"""Example 3: Session Management.

This example demonstrates building a session store with Valkey/Redis
including session creation, validation, and automatic expiration.

Learning objectives:
- Implement secure session tokens
- Manage session data with hashes
- Handle session expiration
- Implement session invalidation

Prerequisites:
- Valkey running on localhost:6379
- Start with: make infra-up (from repository root)
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import redis


@dataclass
class Session:
    """Session data structure."""

    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    data: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    user_agent: str | None = None


class SessionStore:
    """Redis-backed session store."""

    def __init__(
        self,
        client: redis.Redis[str],
        session_ttl: int = 3600,  # 1 hour default
        prefix: str = "session",
    ) -> None:
        """Initialize session store.

        Args:
            client: Redis client.
            session_ttl: Session TTL in seconds.
            prefix: Key prefix for sessions.
        """
        self._client = client
        self._session_ttl = session_ttl
        self._prefix = prefix

    def _key(self, session_id: str) -> str:
        """Create session key."""
        return f"{self._prefix}:{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Create user sessions set key."""
        return f"{self._prefix}:user:{user_id}"

    def create(
        self,
        user_id: str,
        data: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        """Create a new session.

        Args:
            user_id: User identifier.
            data: Initial session data.
            ip_address: Client IP address.
            user_agent: Client user agent.

        Returns:
            Created session.
        """
        # Generate secure token
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()

        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_accessed=now,
            data=data or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Store session
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
            "data": json.dumps(session.data),
            "ip_address": session.ip_address or "",
            "user_agent": session.user_agent or "",
        }

        key = self._key(session_id)
        self._client.hset(key, mapping=session_data)
        self._client.expire(key, self._session_ttl)

        # Track session for user
        self._client.sadd(self._user_sessions_key(user_id), session_id)

        return session

    def get(self, session_id: str, refresh: bool = True) -> Session | None:
        """Get session by ID.

        Args:
            session_id: Session identifier.
            refresh: Whether to refresh TTL and last_accessed.

        Returns:
            Session or None if not found/expired.
        """
        key = self._key(session_id)
        data = self._client.hgetall(key)

        if not data:
            return None

        session = Session(
            session_id=data["session_id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            data=json.loads(data["data"]),
            ip_address=data["ip_address"] or None,
            user_agent=data["user_agent"] or None,
        )

        if refresh:
            # Update last accessed and refresh TTL
            now = datetime.utcnow()
            self._client.hset(key, "last_accessed", now.isoformat())
            self._client.expire(key, self._session_ttl)
            session.last_accessed = now

        return session

    def update_data(self, session_id: str, data: dict[str, Any]) -> bool:
        """Update session data.

        Args:
            session_id: Session identifier.
            data: Data to merge into session.

        Returns:
            True if session exists and was updated.
        """
        key = self._key(session_id)

        if not self._client.exists(key):
            return False

        # Get existing data
        existing = self._client.hget(key, "data")
        if existing:
            merged = json.loads(existing)
            merged.update(data)
        else:
            merged = data

        # Update
        pipe = self._client.pipeline()
        pipe.hset(key, "data", json.dumps(merged))
        pipe.hset(key, "last_accessed", datetime.utcnow().isoformat())
        pipe.expire(key, self._session_ttl)
        pipe.execute()

        return True

    def delete(self, session_id: str) -> bool:
        """Delete a session (logout).

        Args:
            session_id: Session identifier.

        Returns:
            True if session was deleted.
        """
        key = self._key(session_id)

        # Get user_id to remove from user's sessions set
        user_id = self._client.hget(key, "user_id")
        if user_id:
            self._client.srem(self._user_sessions_key(user_id), session_id)

        return self._client.delete(key) > 0

    def delete_all_for_user(self, user_id: str) -> int:
        """Delete all sessions for a user (force logout).

        Args:
            user_id: User identifier.

        Returns:
            Number of sessions deleted.
        """
        sessions_key = self._user_sessions_key(user_id)
        session_ids = self._client.smembers(sessions_key)

        deleted = 0
        for session_id in session_ids:
            if self._client.delete(self._key(session_id)) > 0:
                deleted += 1

        self._client.delete(sessions_key)
        return deleted

    def get_user_sessions(self, user_id: str) -> list[Session]:
        """Get all active sessions for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of active sessions.
        """
        sessions_key = self._user_sessions_key(user_id)
        session_ids = self._client.smembers(sessions_key)

        sessions = []
        for session_id in session_ids:
            session = self.get(session_id, refresh=False)
            if session:
                sessions.append(session)
            else:
                # Clean up expired session reference
                self._client.srem(sessions_key, session_id)

        return sessions

    def count_active(self) -> int:
        """Count total active sessions."""
        count = 0
        for _ in self._client.scan_iter(match=f"{self._prefix}:*"):
            count += 1
        # Subtract user session sets
        for _ in self._client.scan_iter(match=f"{self._prefix}:user:*"):
            count -= 1
        return count


def main() -> None:
    print("=" * 60)
    print("Example 3: Session Management")
    print("=" * 60)

    try:
        client: redis.Redis[str] = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
        )
        client.ping()
        print("\n[OK] Connected to Valkey")
    except redis.ConnectionError as e:
        print(f"\n[ERROR] Could not connect: {e}")
        print("\nMake sure Valkey is running:")
        print("  cd ../../.. && make infra-up")
        return

    # Clean up
    for key in client.scan_iter(match="session:*"):
        client.delete(key)

    # Create session store with 10 second TTL for demo
    store = SessionStore(client, session_ttl=10, prefix="session")

    # Part 1: Create Sessions
    print("\n" + "-" * 40)
    print("PART 1: Creating Sessions")
    print("-" * 40)

    session1 = store.create(
        user_id="user-123",
        data={"theme": "dark", "language": "en"},
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
    )
    print(f"\n  Created session for user-123:")
    print(f"    Session ID: {session1.session_id[:20]}...")
    print(f"    Created at: {session1.created_at}")
    print(f"    Data: {session1.data}")

    session2 = store.create(
        user_id="user-123",
        data={"device": "mobile"},
        ip_address="10.0.0.1",
    )
    print(f"\n  Created second session for user-123:")
    print(f"    Session ID: {session2.session_id[:20]}...")

    # Part 2: Retrieve Sessions
    print("\n" + "-" * 40)
    print("PART 2: Retrieving Sessions")
    print("-" * 40)

    retrieved = store.get(session1.session_id)
    if retrieved:
        print(f"\n  Retrieved session:")
        print(f"    User: {retrieved.user_id}")
        print(f"    Data: {retrieved.data}")
        print(f"    IP: {retrieved.ip_address}")

    # Part 3: Update Session Data
    print("\n" + "-" * 40)
    print("PART 3: Updating Session Data")
    print("-" * 40)

    print("\n  Adding cart to session...")
    store.update_data(session1.session_id, {"cart": ["item-1", "item-2"]})

    retrieved = store.get(session1.session_id)
    if retrieved:
        print(f"    Updated data: {retrieved.data}")

    # Part 4: User Sessions
    print("\n" + "-" * 40)
    print("PART 4: Managing User Sessions")
    print("-" * 40)

    user_sessions = store.get_user_sessions("user-123")
    print(f"\n  Active sessions for user-123: {len(user_sessions)}")
    for s in user_sessions:
        print(f"    - {s.session_id[:20]}... ({s.ip_address})")

    # Part 5: Session Logout
    print("\n" + "-" * 40)
    print("PART 5: Session Logout")
    print("-" * 40)

    print(f"\n  Deleting session 2...")
    deleted = store.delete(session2.session_id)
    print(f"    Deleted: {deleted}")

    user_sessions = store.get_user_sessions("user-123")
    print(f"    Remaining sessions: {len(user_sessions)}")

    # Part 6: Session Expiration
    print("\n" + "-" * 40)
    print("PART 6: Session Expiration (TTL=10s)")
    print("-" * 40)

    print("\n  Checking session over time...")
    for i in range(12):
        session = store.get(session1.session_id, refresh=False)
        ttl = client.ttl(f"session:{session1.session_id}")
        status = "ACTIVE" if session else "EXPIRED"
        print(f"    {i}s: {status} (TTL: {ttl}s)")
        if not session:
            break
        time.sleep(1)

    # Part 7: Force Logout All
    print("\n" + "-" * 40)
    print("PART 7: Force Logout All Sessions")
    print("-" * 40)

    # Create some new sessions
    store.create(user_id="user-456", data={})
    store.create(user_id="user-456", data={})
    store.create(user_id="user-456", data={})

    print(f"\n  Sessions for user-456: {len(store.get_user_sessions('user-456'))}")

    print("  Force logging out user-456...")
    deleted = store.delete_all_for_user("user-456")
    print(f"    Deleted {deleted} sessions")

    print(f"  Sessions for user-456: {len(store.get_user_sessions('user-456'))}")

    # Cleanup
    print("\n" + "-" * 40)
    print("Cleanup")
    print("-" * 40)
    deleted = 0
    for key in client.scan_iter(match="session:*"):
        client.delete(key)
        deleted += 1
    print(f"  Deleted {deleted} keys")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

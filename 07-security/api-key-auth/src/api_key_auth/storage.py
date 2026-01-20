"""API key storage utilities.

This module provides secure storage for API keys with hashing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


def hash_key(key: str) -> str:
    """Hash an API key for storage.

    Uses SHA-256 which is fast but secure for high-entropy keys.
    Unlike passwords, we don't need slow hashing because API keys
    have sufficient entropy to prevent brute-force attacks.

    Args:
        key: The API key to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def verify_key(key: str, key_hash: str) -> bool:
    """Verify an API key against its stored hash.

    Args:
        key: The API key to verify
        key_hash: The stored hash

    Returns:
        True if key matches hash
    """
    return hash_key(key) == key_hash


class KeyStatus(Enum):
    """Status of an API key."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class KeyTier(Enum):
    """API key tier for rate limiting."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class APIKeyInfo:
    """Information about a stored API key."""

    id: str
    key_hash: str
    key_prefix: str  # For display (e.g., "sk_example_FAKE...")
    name: str
    owner_id: str | None = None
    tier: KeyTier = KeyTier.FREE
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if key is currently active."""
        if self.status != KeyStatus.ACTIVE:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    @property
    def is_expired(self) -> bool:
        """Check if key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_revoked(self) -> bool:
        """Check if key has been revoked."""
        return self.status == KeyStatus.REVOKED


class KeyStore:
    """In-memory API key store.

    In production, replace with database-backed storage.
    """

    def __init__(self):
        """Initialize the key store."""
        self._keys: dict[str, APIKeyInfo] = {}  # hash -> info
        self._key_ids: dict[str, str] = {}  # id -> hash

    def store(
        self,
        key: str,
        name: str,
        owner_id: str | None = None,
        tier: KeyTier = KeyTier.FREE,
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> APIKeyInfo:
        """Store a new API key.

        Args:
            key: The raw API key (will be hashed)
            name: Human-readable name for the key
            owner_id: Optional owner identifier
            tier: Key tier for rate limiting
            expires_at: Optional expiration datetime
            metadata: Optional additional metadata

        Returns:
            APIKeyInfo for the stored key
        """
        from api_key_auth.generator import get_key_prefix

        key_hash = hash_key(key)

        # Generate a short ID from the hash
        key_id = key_hash[:16]

        info = APIKeyInfo(
            id=key_id,
            key_hash=key_hash,
            key_prefix=get_key_prefix(key),
            name=name,
            owner_id=owner_id,
            tier=tier,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        self._keys[key_hash] = info
        self._key_ids[key_id] = key_hash

        return info

    def get_by_key(self, key: str) -> APIKeyInfo | None:
        """Get key info by raw key.

        Args:
            key: The raw API key

        Returns:
            APIKeyInfo or None if not found
        """
        key_hash = hash_key(key)
        info = self._keys.get(key_hash)

        if info:
            # Update last used timestamp
            info.last_used_at = datetime.utcnow()

        return info

    def get_by_id(self, key_id: str) -> APIKeyInfo | None:
        """Get key info by ID.

        Args:
            key_id: The key ID

        Returns:
            APIKeyInfo or None if not found
        """
        key_hash = self._key_ids.get(key_id)
        if key_hash:
            return self._keys.get(key_hash)
        return None

    def revoke(self, key_id: str, reason: str | None = None) -> bool:
        """Revoke an API key.

        Args:
            key_id: The key ID to revoke
            reason: Optional revocation reason

        Returns:
            True if key was revoked
        """
        info = self.get_by_id(key_id)
        if info:
            info.status = KeyStatus.REVOKED
            if reason:
                info.metadata["revocation_reason"] = reason
                info.metadata["revoked_at"] = datetime.utcnow().isoformat()
            return True
        return False

    def delete(self, key_id: str) -> bool:
        """Delete an API key.

        Args:
            key_id: The key ID to delete

        Returns:
            True if key was deleted
        """
        key_hash = self._key_ids.get(key_id)
        if key_hash:
            del self._keys[key_hash]
            del self._key_ids[key_id]
            return True
        return False

    def list_keys(
        self,
        owner_id: str | None = None,
        status: KeyStatus | None = None,
        tier: KeyTier | None = None,
    ) -> list[APIKeyInfo]:
        """List API keys with optional filters.

        Args:
            owner_id: Filter by owner
            status: Filter by status
            tier: Filter by tier

        Returns:
            List of matching APIKeyInfo
        """
        results = []
        for info in self._keys.values():
            if owner_id and info.owner_id != owner_id:
                continue
            if status and info.status != status:
                continue
            if tier and info.tier != tier:
                continue
            results.append(info)
        return results

    def update_tier(self, key_id: str, tier: KeyTier) -> bool:
        """Update the tier for a key.

        Args:
            key_id: The key ID
            tier: New tier

        Returns:
            True if updated
        """
        info = self.get_by_id(key_id)
        if info:
            info.tier = tier
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove expired keys from storage.

        Returns:
            Number of keys removed
        """
        now = datetime.utcnow()
        expired_hashes = [
            key_hash
            for key_hash, info in self._keys.items()
            if info.expires_at and info.expires_at < now
        ]

        for key_hash in expired_hashes:
            info = self._keys[key_hash]
            del self._keys[key_hash]
            del self._key_ids[info.id]

        return len(expired_hashes)

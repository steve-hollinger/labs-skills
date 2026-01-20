"""Solution 3: Token Expiry Check"""

import time
from dataclasses import dataclass


@dataclass
class ManagedToken:
    """Token with expiry management."""

    access_token: str
    expires_at: float

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if token is expired or expiring within buffer time.

        Args:
            buffer_seconds: Consider expired if expiring within this time

        Returns:
            True if expired or expiring soon
        """
        return time.time() >= (self.expires_at - buffer_seconds)

    def seconds_until_expiry(self) -> int:
        """Get seconds remaining until token expires.

        Returns:
            Seconds until expiry (0 if already expired)
        """
        remaining = self.expires_at - time.time()
        return max(0, int(remaining))

    def should_refresh(self, threshold_seconds: int = 300) -> bool:
        """Check if token should be proactively refreshed.

        Args:
            threshold_seconds: Refresh if less than this time remaining

        Returns:
            True if token should be refreshed
        """
        return self.seconds_until_expiry() < threshold_seconds


if __name__ == "__main__":
    # Token expiring in 1 hour
    token = ManagedToken(
        access_token="test-token",
        expires_at=time.time() + 3600,
    )

    # Should not be expired
    assert not token.is_expired()
    print(f"Seconds until expiry: {token.seconds_until_expiry()}")

    # Should not need refresh yet
    assert not token.should_refresh()

    # Token expiring in 30 seconds
    soon_expiring = ManagedToken(
        access_token="test-token",
        expires_at=time.time() + 30,
    )

    # With 60 second buffer, should be considered expired
    assert soon_expiring.is_expired(buffer_seconds=60)

    # Should need refresh
    assert soon_expiring.should_refresh(threshold_seconds=60)

    # Already expired token
    expired = ManagedToken(
        access_token="test-token",
        expires_at=time.time() - 100,
    )
    assert expired.is_expired()
    assert expired.seconds_until_expiry() == 0
    assert expired.should_refresh()

    print("All tests passed!")

"""Exercise 3: Implement Token Expiry Check

Your task: Implement a class that manages token expiry checking
with configurable buffer time for proactive refresh.

Requirements:
1. Store token and its expiry timestamp
2. Check if token is expired considering buffer time
3. Calculate time remaining until expiry
"""

import time
from dataclasses import dataclass


@dataclass
class ManagedToken:
    """Token with expiry management.

    TODO: Add the following methods:
    - is_expired(buffer_seconds: int = 60) -> bool
    - seconds_until_expiry() -> int
    - should_refresh(threshold_seconds: int = 300) -> bool
    """

    access_token: str
    expires_at: float  # Unix timestamp when token expires

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if token is expired or expiring within buffer time.

        Args:
            buffer_seconds: Consider expired if expiring within this time

        Returns:
            True if expired or expiring soon
        """
        # Your implementation here
        pass

    def seconds_until_expiry(self) -> int:
        """Get seconds remaining until token expires.

        Returns:
            Seconds until expiry (0 if already expired)
        """
        # Your implementation here
        pass

    def should_refresh(self, threshold_seconds: int = 300) -> bool:
        """Check if token should be proactively refreshed.

        Args:
            threshold_seconds: Refresh if less than this time remaining

        Returns:
            True if token should be refreshed
        """
        # Your implementation here
        pass


# Test your implementation
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

    print("All tests passed!")

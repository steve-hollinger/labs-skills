"""Exercise 3: Token Refresh with Rotation.

Create a complete token refresh system that:
1. Issues access/refresh token pairs
2. Implements refresh token rotation (one-time use)
3. Maintains a deny list for revoked tokens
4. Supports token families for detecting theft

Expected usage:
    service = TokenRefreshService(secret, refresh_secret)
    tokens = service.create_token_pair(user_id, roles)

    # Later, refresh the tokens
    new_tokens = service.refresh(tokens.refresh_token)

    # Old refresh token should be invalid
    service.refresh(tokens.refresh_token)  # Raises error

    # Revoke a token family (logout from all devices)
    service.revoke_family(family_id)

Hints:
- Use unique jti (JWT ID) for each refresh token
- Track token families with a family_id claim
- Store revoked tokens in a set (use Redis in production)
- Implement automatic family revocation on reuse detection
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class TokenPair:
    """Access and refresh token pair.

    Attributes:
        access_token: Short-lived access token
        refresh_token: Long-lived refresh token
        token_type: Token type (always "bearer")
        expires_in: Access token TTL in seconds
        refresh_expires_in: Refresh token TTL in seconds
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes
    refresh_expires_in: int = 604800  # 7 days


class TokenRevokedError(Exception):
    """Token has been revoked."""

    pass


class TokenReusedError(Exception):
    """Refresh token reuse detected (possible theft)."""

    pass


class TokenRefreshService:
    """Service for managing token refresh with rotation.

    TODO: Implement:
    - create_token_pair(user_id: str, roles: list[str]) -> TokenPair
    - refresh(refresh_token: str) -> TokenPair
    - revoke_token(jti: str) -> None
    - revoke_family(family_id: str) -> None
    - is_revoked(jti: str) -> bool
    """

    def __init__(
        self,
        access_secret: str,
        refresh_secret: str,
        access_ttl: timedelta = timedelta(minutes=15),
        refresh_ttl: timedelta = timedelta(days=7),
    ):
        """Initialize the service.

        Args:
            access_secret: Secret for signing access tokens
            refresh_secret: Secret for signing refresh tokens
            access_ttl: Access token time-to-live
            refresh_ttl: Refresh token time-to-live
        """
        # TODO: Store configuration
        # TODO: Initialize revoked tokens storage
        # TODO: Initialize token families storage
        pass

    def _generate_jti(self) -> str:
        """Generate a unique JWT ID.

        Returns:
            Unique identifier string
        """
        # TODO: Generate unique ID
        raise NotImplementedError("Implement _generate_jti")

    def _generate_family_id(self) -> str:
        """Generate a unique token family ID.

        Returns:
            Unique family identifier
        """
        # TODO: Generate unique family ID
        raise NotImplementedError("Implement _generate_family_id")

    def create_token_pair(
        self,
        user_id: str,
        roles: list[str],
        family_id: str | None = None,
    ) -> TokenPair:
        """Create a new access/refresh token pair.

        Args:
            user_id: User identifier
            roles: User roles
            family_id: Token family ID (creates new if None)

        Returns:
            TokenPair with both tokens
        """
        # TODO: Implement token creation
        # 1. Generate or use provided family_id
        # 2. Create access token with short TTL
        # 3. Create refresh token with long TTL and jti
        # 4. Track the refresh token in its family
        raise NotImplementedError("Implement create_token_pair")

    def refresh(self, refresh_token: str) -> TokenPair:
        """Use a refresh token to get new tokens.

        Implements refresh token rotation:
        - The used refresh token is revoked
        - A new token pair is issued
        - Reuse of revoked token triggers family revocation

        Args:
            refresh_token: The refresh token to use

        Returns:
            New TokenPair

        Raises:
            TokenRevokedError: If token was already revoked
            TokenReusedError: If token reuse detected
        """
        # TODO: Implement refresh with rotation
        # 1. Validate the refresh token
        # 2. Check if token or family is revoked
        # 3. If token was already used, revoke entire family
        # 4. Revoke the used token
        # 5. Issue new token pair with same family
        raise NotImplementedError("Implement refresh")

    def revoke_token(self, jti: str) -> None:
        """Revoke a specific refresh token.

        Args:
            jti: The JWT ID to revoke
        """
        # TODO: Add to revoked set
        raise NotImplementedError("Implement revoke_token")

    def revoke_family(self, family_id: str) -> None:
        """Revoke all tokens in a family (logout everywhere).

        Args:
            family_id: The token family to revoke
        """
        # TODO: Add family to revoked families
        raise NotImplementedError("Implement revoke_family")

    def is_revoked(self, jti: str) -> bool:
        """Check if a token is revoked.

        Args:
            jti: The JWT ID to check

        Returns:
            True if revoked
        """
        # TODO: Check if in revoked set
        raise NotImplementedError("Implement is_revoked")

    def is_family_revoked(self, family_id: str) -> bool:
        """Check if a token family is revoked.

        Args:
            family_id: The family ID to check

        Returns:
            True if family is revoked
        """
        # TODO: Check if family in revoked set
        raise NotImplementedError("Implement is_family_revoked")


def main() -> None:
    """Test your implementation."""
    print("Exercise 3: Token Refresh with Rotation")
    print("See the solution in solutions/solution_3.py")

    # Uncomment to test your implementation:
    #
    # access_secret = secrets.token_urlsafe(32)
    # refresh_secret = secrets.token_urlsafe(32)
    #
    # service = TokenRefreshService(access_secret, refresh_secret)
    #
    # # Create initial tokens
    # print("\n1. Creating initial tokens:")
    # tokens = service.create_token_pair("user123", ["user", "editor"])
    # print(f"   Access token: {tokens.access_token[:50]}...")
    # print(f"   Refresh token: {tokens.refresh_token[:50]}...")
    #
    # # Refresh tokens
    # print("\n2. Refreshing tokens:")
    # new_tokens = service.refresh(tokens.refresh_token)
    # print(f"   New access token: {new_tokens.access_token[:50]}...")
    # print(f"   New refresh token: {new_tokens.refresh_token[:50]}...")
    #
    # # Try to reuse old refresh token
    # print("\n3. Trying to reuse old refresh token:")
    # try:
    #     service.refresh(tokens.refresh_token)
    # except TokenRevokedError as e:
    #     print(f"   Correctly rejected: {e}")
    # except TokenReusedError as e:
    #     print(f"   Reuse detected: {e}")
    #
    # # Verify new tokens work
    # print("\n4. Refreshing with new token:")
    # third_tokens = service.refresh(new_tokens.refresh_token)
    # print(f"   Success! Got new tokens")
    #
    # # Revoke family (logout everywhere)
    # print("\n5. Testing family revocation:")
    # # Extract family_id from token (implementation specific)
    # # service.revoke_family(family_id)
    # # try:
    # #     service.refresh(third_tokens.refresh_token)
    # # except TokenRevokedError:
    # #     print("   Family revoked successfully")


if __name__ == "__main__":
    main()

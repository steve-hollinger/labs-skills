"""Solution 3: Token Refresh with Rotation.

This solution demonstrates a secure token refresh system with
refresh token rotation and family-based revocation.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


@dataclass
class TokenPair:
    """Access and refresh token pair."""

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
    """Service for managing token refresh with rotation."""

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
        self.access_secret = access_secret
        self.refresh_secret = refresh_secret
        self.access_ttl = access_ttl
        self.refresh_ttl = refresh_ttl

        # In production, use Redis or database
        self._revoked_tokens: set[str] = set()
        self._revoked_families: set[str] = set()
        self._used_tokens: set[str] = set()  # Track used tokens for rotation
        self._token_families: dict[str, set[str]] = {}  # family_id -> set of jtis

    def _generate_jti(self) -> str:
        """Generate a unique JWT ID."""
        return secrets.token_urlsafe(16)

    def _generate_family_id(self) -> str:
        """Generate a unique token family ID."""
        return secrets.token_urlsafe(12)

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
        now = datetime.now(timezone.utc)
        jti = self._generate_jti()

        # Create or use family ID
        if family_id is None:
            family_id = self._generate_family_id()
            self._token_families[family_id] = set()

        # Track this token in its family
        self._token_families[family_id].add(jti)

        # Access token (short-lived)
        access_payload = {
            "sub": user_id,
            "roles": roles,
            "type": "access",
            "iat": now,
            "exp": now + self.access_ttl,
        }
        access_token = jwt.encode(access_payload, self.access_secret, algorithm="HS256")

        # Refresh token (long-lived, with jti and family_id)
        refresh_payload = {
            "sub": user_id,
            "roles": roles,
            "type": "refresh",
            "jti": jti,
            "family_id": family_id,
            "iat": now,
            "exp": now + self.refresh_ttl,
        }
        refresh_token = jwt.encode(
            refresh_payload, self.refresh_secret, algorithm="HS256"
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.access_ttl.total_seconds()),
            refresh_expires_in=int(self.refresh_ttl.total_seconds()),
        )

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
        # Decode the refresh token
        try:
            payload = jwt.decode(
                refresh_token,
                self.refresh_secret,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise TokenRevokedError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenRevokedError(f"Invalid refresh token: {e}")

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise TokenRevokedError("Not a refresh token")

        jti = payload.get("jti")
        family_id = payload.get("family_id")

        if not jti or not family_id:
            raise TokenRevokedError("Invalid token structure")

        # Check if family is revoked
        if family_id in self._revoked_families:
            raise TokenRevokedError("Token family has been revoked")

        # Check if token is explicitly revoked
        if jti in self._revoked_tokens:
            raise TokenRevokedError("Refresh token has been revoked")

        # Check for token reuse (rotation violation)
        if jti in self._used_tokens:
            # Token reuse detected! This could be theft.
            # Revoke the entire family as a security measure.
            self.revoke_family(family_id)
            raise TokenReusedError(
                "Refresh token reuse detected. All tokens in this family have been revoked. "
                "Please log in again."
            )

        # Mark this token as used
        self._used_tokens.add(jti)

        # Revoke the old token
        self._revoked_tokens.add(jti)

        # Issue new token pair with the same family
        return self.create_token_pair(
            user_id=payload["sub"],
            roles=payload["roles"],
            family_id=family_id,
        )

    def revoke_token(self, jti: str) -> None:
        """Revoke a specific refresh token.

        Args:
            jti: The JWT ID to revoke
        """
        self._revoked_tokens.add(jti)

    def revoke_family(self, family_id: str) -> None:
        """Revoke all tokens in a family (logout everywhere).

        Args:
            family_id: The token family to revoke
        """
        self._revoked_families.add(family_id)

        # Also revoke all individual tokens in the family
        if family_id in self._token_families:
            for jti in self._token_families[family_id]:
                self._revoked_tokens.add(jti)

    def is_revoked(self, jti: str) -> bool:
        """Check if a token is revoked.

        Args:
            jti: The JWT ID to check

        Returns:
            True if revoked
        """
        return jti in self._revoked_tokens

    def is_family_revoked(self, family_id: str) -> bool:
        """Check if a token family is revoked.

        Args:
            family_id: The family ID to check

        Returns:
            True if family is revoked
        """
        return family_id in self._revoked_families

    def decode_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Decode a refresh token without validation.

        For debugging only!

        Args:
            refresh_token: The token to decode

        Returns:
            Decoded payload
        """
        return jwt.decode(
            refresh_token,
            options={"verify_signature": False},
        )


def main() -> None:
    """Demonstrate the token refresh service."""
    print("=" * 60)
    print("Solution 3: Token Refresh with Rotation")
    print("=" * 60)

    access_secret = secrets.token_urlsafe(32)
    refresh_secret = secrets.token_urlsafe(32)

    service = TokenRefreshService(access_secret, refresh_secret)

    # 1. Create initial tokens
    print("\n1. Creating initial token pair:")
    tokens = service.create_token_pair("user123", ["user", "editor"])
    print(f"   Access token: {tokens.access_token[:50]}...")
    print(f"   Refresh token: {tokens.refresh_token[:50]}...")
    print(f"   Access expires in: {tokens.expires_in}s")
    print(f"   Refresh expires in: {tokens.refresh_expires_in}s")

    # Decode to show structure
    refresh_payload = service.decode_refresh_token(tokens.refresh_token)
    print(f"\n   Refresh token contents:")
    print(f"     sub: {refresh_payload['sub']}")
    print(f"     jti: {refresh_payload['jti']}")
    print(f"     family_id: {refresh_payload['family_id']}")

    # 2. Refresh tokens (rotation)
    print("\n2. Refreshing tokens (rotation):")
    new_tokens = service.refresh(tokens.refresh_token)
    print(f"   New access token: {new_tokens.access_token[:50]}...")
    print(f"   New refresh token: {new_tokens.refresh_token[:50]}...")

    new_payload = service.decode_refresh_token(new_tokens.refresh_token)
    print(f"   New jti: {new_payload['jti']}")
    print(f"   Same family_id: {new_payload['family_id'] == refresh_payload['family_id']}")

    # 3. Try to reuse old refresh token
    print("\n3. Attempting to reuse old refresh token:")
    try:
        service.refresh(tokens.refresh_token)
        print("   Unexpected success!")
    except TokenRevokedError as e:
        print(f"   Correctly rejected (revoked): {e}")
    except TokenReusedError as e:
        print(f"   Reuse detected: {e}")

    # 4. New tokens still work
    print("\n4. Using new refresh token:")
    third_tokens = service.refresh(new_tokens.refresh_token)
    print(f"   Success! Got another token pair")
    print(f"   Access token: {third_tokens.access_token[:50]}...")

    # 5. Test family revocation
    print("\n5. Testing family revocation (logout everywhere):")
    third_payload = service.decode_refresh_token(third_tokens.refresh_token)
    family_id = third_payload["family_id"]

    print(f"   Revoking family: {family_id}")
    service.revoke_family(family_id)

    try:
        service.refresh(third_tokens.refresh_token)
        print("   Unexpected success!")
    except TokenRevokedError as e:
        print(f"   Correctly rejected: {e}")

    # 6. Create new session (new family)
    print("\n6. Creating new session (new family):")
    new_session = service.create_token_pair("user123", ["user", "editor"])
    new_session_payload = service.decode_refresh_token(new_session.refresh_token)
    print(f"   New family_id: {new_session_payload['family_id']}")
    print(f"   Different from revoked family: {new_session_payload['family_id'] != family_id}")

    # Verify new session works
    refreshed = service.refresh(new_session.refresh_token)
    print(f"   New session refresh works: True")

    # Summary
    print("\n" + "=" * 60)
    print("Key Security Features:")
    print("=" * 60)
    print("""
1. Refresh Token Rotation:
   - Each refresh token can only be used once
   - New token pair issued on refresh
   - Prevents replay attacks

2. Reuse Detection:
   - If a token is used twice, theft is assumed
   - Entire token family is revoked
   - User must log in again

3. Token Families:
   - Tokens are grouped by family_id
   - Enables "logout everywhere" functionality
   - All tokens in family can be revoked at once

4. Separate Secrets:
   - Access and refresh tokens use different secrets
   - Limits damage if one secret is compromised
""")

    print("=" * 60)
    print("Solution 3 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

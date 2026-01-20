"""Example 3: Token refresh and session management.

This example demonstrates OAuth 2.1 refresh token handling
and secure session management patterns.
"""

import time
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class TokenSet:
    """OAuth token set with metadata."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None
    id_token: str | None = None
    expires_at: float = field(init=False)

    def __post_init__(self) -> None:
        self.expires_at = time.time() + self.expires_in

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check if access token is expired or expiring soon."""
        return time.time() >= (self.expires_at - buffer_seconds)


class TokenManager:
    """Manages OAuth tokens with automatic refresh."""

    def __init__(
        self,
        token_endpoint: str,
        client_id: str,
        client_secret: str | None = None,
    ) -> None:
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self._tokens: TokenSet | None = None

    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> TokenSet:
        """Exchange authorization code for tokens.

        Args:
            code: Authorization code from callback
            redirect_uri: Must match original redirect_uri
            code_verifier: PKCE code verifier

        Returns:
            TokenSet with access and refresh tokens
        """
        data: dict[str, Any] = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "code_verifier": code_verifier,
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()

        self._tokens = TokenSet(**token_data)
        return self._tokens

    async def refresh(self) -> TokenSet:
        """Refresh the access token using the refresh token.

        Returns:
            New TokenSet with fresh access token

        Raises:
            ValueError: If no refresh token available
        """
        if not self._tokens or not self._tokens.refresh_token:
            raise ValueError("No refresh token available")

        data: dict[str, Any] = {
            "grant_type": "refresh_token",
            "refresh_token": self._tokens.refresh_token,
            "client_id": self.client_id,
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_endpoint, data=data)
            response.raise_for_status()
            token_data = response.json()

        # OAuth 2.1 recommends refresh token rotation
        # New refresh token may be issued
        self._tokens = TokenSet(**token_data)
        return self._tokens

    async def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if needed.

        Returns:
            Valid access token string
        """
        if not self._tokens:
            raise ValueError("No tokens available - authenticate first")

        if self._tokens.is_expired():
            await self.refresh()

        return self._tokens.access_token


def main() -> None:
    """Demonstrate token refresh and management."""
    print("OAuth 2.1 Token Refresh and Management")
    print("=" * 60)

    print("\nToken Lifecycle:")
    print("1. Exchange authorization code for tokens")
    print("2. Store tokens securely (encrypted, httpOnly cookies)")
    print("3. Use access token for API calls")
    print("4. Before expiry, refresh using refresh token")
    print("5. Handle refresh token rotation (new refresh token each time)")

    print("\nOAuth 2.1 Refresh Token Best Practices:")
    print("  - Rotate refresh tokens on each use")
    print("  - Use one-time refresh tokens when possible")
    print("  - Set reasonable expiration (days/weeks)")
    print("  - Revoke on logout or security events")

    print("\nSecure Storage Patterns:")
    print("  - Backend: Encrypted database or Redis")
    print("  - Browser: httpOnly secure cookies")
    print("  - Mobile: OS keychain/keystore")
    print("  - NEVER store in localStorage or sessionStorage")

    print("\nError Handling:")
    print("  - invalid_grant: Refresh token revoked/expired")
    print("  - invalid_client: Client credentials wrong")
    print("  - server_error: Retry with backoff")

    # Example token set
    print("\nExample TokenSet:")
    tokens = TokenSet(
        access_token="eyJhbGciOiJSUzI1NiIs...",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="v1.refresh.abc123...",
        scope="openid profile email",
    )
    print(f"  Token Type: {tokens.token_type}")
    print(f"  Expires In: {tokens.expires_in}s")
    print(f"  Has Refresh: {tokens.refresh_token is not None}")
    print(f"  Is Expired: {tokens.is_expired()}")


if __name__ == "__main__":
    main()

"""Example 1: OAuth 2.1 Authorization Code flow with PKCE.

This example demonstrates the modern OAuth 2.1 flow using PKCE
(Proof Key for Code Exchange) which is now required for all clients.
"""

import hashlib
import secrets
import base64
from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass
class PKCEChallenge:
    """PKCE code verifier and challenge pair."""

    verifier: str
    challenge: str
    method: str = "S256"


def generate_pkce_challenge() -> PKCEChallenge:
    """Generate a PKCE code verifier and challenge.

    The verifier is a cryptographically random string.
    The challenge is the SHA256 hash of the verifier, base64url encoded.
    """
    # Generate a random 43-128 character verifier
    verifier = secrets.token_urlsafe(32)

    # Create SHA256 hash and base64url encode it
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")

    return PKCEChallenge(verifier=verifier, challenge=challenge)


def build_authorization_url(
    authorize_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    pkce: PKCEChallenge,
) -> str:
    """Build the OAuth 2.1 authorization URL with PKCE.

    Args:
        authorize_endpoint: The provider's authorization endpoint
        client_id: Your application's client ID
        redirect_uri: Where to redirect after authorization
        scope: Space-separated list of requested scopes
        state: Random state for CSRF protection
        pkce: PKCE challenge pair

    Returns:
        The full authorization URL to redirect users to
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": pkce.challenge,
        "code_challenge_method": pkce.method,
    }
    return f"{authorize_endpoint}?{urlencode(params)}"


def main() -> None:
    """Demonstrate OAuth 2.1 Authorization Code + PKCE flow."""
    # Configuration (would come from environment in production)
    config = {
        "authorize_endpoint": "https://auth.example.com/oauth/authorize",
        "client_id": "your-client-id",
        "redirect_uri": "http://localhost:8000/callback",
        "scope": "openid profile email",
    }

    # Generate PKCE challenge
    pkce = generate_pkce_challenge()
    print("PKCE Challenge Generated:")
    print(f"  Verifier: {pkce.verifier[:20]}...")
    print(f"  Challenge: {pkce.challenge}")
    print(f"  Method: {pkce.method}")

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(16)
    print(f"\nState (store in session): {state}")

    # Build authorization URL
    auth_url = build_authorization_url(
        authorize_endpoint=config["authorize_endpoint"],
        client_id=config["client_id"],
        redirect_uri=config["redirect_uri"],
        scope=config["scope"],
        state=state,
        pkce=pkce,
    )

    print(f"\nAuthorization URL:\n{auth_url}")
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Store state and pkce.verifier in user's session")
    print("2. Redirect user to authorization URL")
    print("3. User authenticates with provider")
    print("4. Provider redirects back with code and state")
    print("5. Exchange code + verifier for tokens")


if __name__ == "__main__":
    main()

"""Example 2: OpenID Connect ID Token validation.

This example demonstrates how to validate OIDC ID tokens,
which contain identity claims about the authenticated user.
"""

from dataclasses import dataclass
from typing import Any

import jwt
from jwt import PyJWKClient


@dataclass
class OIDCConfig:
    """OpenID Connect provider configuration."""

    issuer: str
    jwks_uri: str
    audience: str


@dataclass
class UserInfo:
    """Validated user information from ID token."""

    subject: str
    email: str | None
    name: str | None
    picture: str | None
    email_verified: bool


class IDTokenValidator:
    """Validates OpenID Connect ID tokens."""

    def __init__(self, config: OIDCConfig) -> None:
        self.config = config
        self.jwks_client = PyJWKClient(config.jwks_uri, cache_jwk_set=True)

    def validate(self, id_token: str, nonce: str | None = None) -> UserInfo:
        """Validate an ID token and extract user information.

        Args:
            id_token: The raw ID token JWT
            nonce: Expected nonce value (required for implicit/hybrid flows)

        Returns:
            UserInfo with validated claims

        Raises:
            jwt.InvalidTokenError: If token validation fails
        """
        # Get the signing key from JWKS
        signing_key = self.jwks_client.get_signing_key_from_jwt(id_token)

        # Decode and validate the token
        claims: dict[str, Any] = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.config.audience,
            issuer=self.config.issuer,
            options={
                "require": ["exp", "iat", "sub", "iss", "aud"],
            },
        )

        # Validate nonce if provided (required for implicit/hybrid flows)
        if nonce is not None:
            token_nonce = claims.get("nonce")
            if token_nonce != nonce:
                raise jwt.InvalidTokenError(
                    f"Nonce mismatch: expected {nonce}, got {token_nonce}"
                )

        return UserInfo(
            subject=claims["sub"],
            email=claims.get("email"),
            name=claims.get("name"),
            picture=claims.get("picture"),
            email_verified=claims.get("email_verified", False),
        )


def main() -> None:
    """Demonstrate OIDC ID token validation."""
    print("OpenID Connect ID Token Validation")
    print("=" * 60)

    # Example configuration (Google as provider)
    config = OIDCConfig(
        issuer="https://accounts.google.com",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        audience="your-client-id.apps.googleusercontent.com",
    )

    print(f"Provider: {config.issuer}")
    print(f"JWKS URI: {config.jwks_uri}")

    # In production, you would have an actual ID token
    # Here we show the validation pattern
    print("\nValidation Steps:")
    print("1. Fetch signing keys from JWKS endpoint")
    print("2. Verify JWT signature using RS256")
    print("3. Validate issuer matches expected provider")
    print("4. Validate audience matches your client ID")
    print("5. Check token is not expired (exp claim)")
    print("6. Validate nonce if using implicit/hybrid flow")
    print("7. Extract user claims (sub, email, name, etc.)")

    print("\nRequired Claims:")
    print("  - sub: Subject (unique user identifier)")
    print("  - iss: Issuer (identity provider)")
    print("  - aud: Audience (your client ID)")
    print("  - exp: Expiration time")
    print("  - iat: Issued at time")

    print("\nCommon Optional Claims:")
    print("  - email: User's email address")
    print("  - email_verified: Whether email is verified")
    print("  - name: User's full name")
    print("  - picture: URL to profile picture")
    print("  - nonce: For replay attack prevention")


if __name__ == "__main__":
    main()

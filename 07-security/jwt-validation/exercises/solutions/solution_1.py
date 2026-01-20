"""Solution 1: JWT Decoder.

This solution demonstrates decoding JWTs for debugging
without validating the signature.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TokenInfo:
    """Information extracted from a JWT."""

    header: dict[str, Any]
    claims: dict[str, Any]

    @property
    def algorithm(self) -> str:
        """Get the signing algorithm."""
        return self.header.get("alg", "unknown")

    @property
    def token_type(self) -> str:
        """Get the token type."""
        return self.header.get("typ", "unknown")

    @property
    def key_id(self) -> str | None:
        """Get the key ID if present."""
        return self.header.get("kid")

    @property
    def subject(self) -> str | None:
        """Get the subject claim."""
        return self.claims.get("sub")

    @property
    def issuer(self) -> str | None:
        """Get the issuer claim."""
        return self.claims.get("iss")

    @property
    def audience(self) -> str | list[str] | None:
        """Get the audience claim."""
        return self.claims.get("aud")

    @property
    def expires_at(self) -> datetime | None:
        """Get expiration as datetime."""
        exp = self.claims.get("exp")
        if exp is None:
            return None
        return datetime.fromtimestamp(exp, tz=timezone.utc)

    @property
    def issued_at(self) -> datetime | None:
        """Get issued at as datetime."""
        iat = self.claims.get("iat")
        if iat is None:
            return None
        return datetime.fromtimestamp(iat, tz=timezone.utc)

    @property
    def not_before(self) -> datetime | None:
        """Get not before as datetime."""
        nbf = self.claims.get("nbf")
        if nbf is None:
            return None
        return datetime.fromtimestamp(nbf, tz=timezone.utc)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        exp = self.expires_at
        if exp is None:
            return False
        return exp < datetime.now(timezone.utc)

    @property
    def expires_in_seconds(self) -> int | None:
        """Get seconds until expiration (negative if expired)."""
        exp = self.expires_at
        if exp is None:
            return None
        now = datetime.now(timezone.utc)
        return int((exp - now).total_seconds())


class JWTDecoder:
    """Decodes JWTs without signature verification.

    WARNING: This is for debugging only. Never trust decoded
    data without verification in production!
    """

    def decode(self, token: str) -> TokenInfo:
        """Decode a JWT and extract information.

        Args:
            token: The JWT string

        Returns:
            TokenInfo with decoded data

        Raises:
            ValueError: If token is malformed
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid JWT format: expected 3 parts separated by '.', got {len(parts)}"
            )

        try:
            header = self._decode_part(parts[0])
            claims = self._decode_part(parts[1])
        except Exception as e:
            raise ValueError(f"Failed to decode JWT: {e}") from e

        return TokenInfo(header=header, claims=claims)

    def _decode_part(self, part: str) -> dict[str, Any]:
        """Decode a base64url-encoded JWT part.

        Args:
            part: The base64url-encoded string

        Returns:
            Decoded JSON as dict
        """
        padded = self._add_base64_padding(part)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)

    def _add_base64_padding(self, data: str) -> str:
        """Add padding to base64 string if needed.

        Args:
            data: The base64 string

        Returns:
            Padded string
        """
        # Base64 requires length to be multiple of 4
        padding_needed = 4 - (len(data) % 4)
        if padding_needed != 4:
            data += "=" * padding_needed
        return data

    def format_info(self, info: TokenInfo) -> str:
        """Format token info for display.

        Args:
            info: The TokenInfo to format

        Returns:
            Human-readable string
        """
        lines = [
            "=" * 50,
            "JWT Token Information",
            "=" * 50,
            "",
            "HEADER:",
            f"  Algorithm: {info.algorithm}",
            f"  Type: {info.token_type}",
        ]

        if info.key_id:
            lines.append(f"  Key ID: {info.key_id}")

        lines.extend([
            "",
            "CLAIMS:",
            f"  Subject: {info.subject or 'N/A'}",
            f"  Issuer: {info.issuer or 'N/A'}",
            f"  Audience: {info.audience or 'N/A'}",
        ])

        lines.extend([
            "",
            "TIME CLAIMS:",
        ])

        if info.issued_at:
            lines.append(f"  Issued At: {info.issued_at.isoformat()}")

        if info.not_before:
            lines.append(f"  Not Before: {info.not_before.isoformat()}")

        if info.expires_at:
            lines.append(f"  Expires At: {info.expires_at.isoformat()}")
            if info.is_expired:
                lines.append(f"  Status: EXPIRED ({-info.expires_in_seconds}s ago)")
            else:
                lines.append(f"  Status: Valid ({info.expires_in_seconds}s remaining)")
        else:
            lines.append("  Expires At: No expiration")

        # Custom claims
        standard_claims = {"sub", "iss", "aud", "exp", "iat", "nbf", "jti"}
        custom_claims = {k: v for k, v in info.claims.items() if k not in standard_claims}

        if custom_claims:
            lines.extend([
                "",
                "CUSTOM CLAIMS:",
            ])
            for key, value in custom_claims.items():
                lines.append(f"  {key}: {value}")

        lines.extend([
            "",
            "=" * 50,
        ])

        return "\n".join(lines)


def main() -> None:
    """Demonstrate the JWT decoder."""
    import secrets
    from datetime import timedelta

    import jwt

    print("=" * 60)
    print("Solution 1: JWT Decoder")
    print("=" * 60)

    # Create a test token
    secret = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "user123",
        "name": "John Doe",
        "email": "john@example.com",
        "roles": ["user", "editor"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": "https://auth.example.com",
        "aud": "my-api",
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    print("\n1. Created test token")
    print(f"   Token: {token[:60]}...")

    # Decode it
    decoder = JWTDecoder()
    info = decoder.decode(token)

    print("\n2. Decoded token info:")
    print(f"   Algorithm: {info.algorithm}")
    print(f"   Subject: {info.subject}")
    print(f"   Issuer: {info.issuer}")
    print(f"   Audience: {info.audience}")
    print(f"   Expires at: {info.expires_at}")
    print(f"   Is expired: {info.is_expired}")
    print(f"   Expires in: {info.expires_in_seconds} seconds")

    print("\n3. Formatted output:")
    print(decoder.format_info(info))

    # Test with expired token
    print("\n4. Testing expired token:")
    expired_payload = {**payload, "exp": now - timedelta(hours=1)}
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")

    expired_info = decoder.decode(expired_token)
    print(f"   Is expired: {expired_info.is_expired}")
    print(f"   Expired {-expired_info.expires_in_seconds} seconds ago")

    # Test with RS256 token
    print("\n5. Testing RS256 token:")
    from jwt_validation import generate_rsa_keypair

    private_key, _ = generate_rsa_keypair()
    rs256_token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": "my-key-id"},
    )

    rs256_info = decoder.decode(rs256_token)
    print(f"   Algorithm: {rs256_info.algorithm}")
    print(f"   Key ID: {rs256_info.key_id}")

    print("\n" + "=" * 60)
    print("Solution 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

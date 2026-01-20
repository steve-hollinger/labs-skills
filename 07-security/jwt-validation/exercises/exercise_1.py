"""Exercise 1: JWT Decoder.

Create a JWT decoder that extracts and displays token information
without validating the signature. This is useful for debugging.

Requirements:
1. Decode the header and payload without verification
2. Display claims in a human-readable format
3. Show expiration status and time remaining
4. Identify the signing algorithm
5. Handle malformed tokens gracefully

Expected usage:
    decoder = JWTDecoder()
    info = decoder.decode("eyJ...")
    print(info.algorithm)
    print(info.claims)
    print(info.expires_in_seconds)

Hints:
- Use base64.urlsafe_b64decode for decoding
- Handle padding for base64 decoding
- Use datetime for time calculations
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class TokenInfo:
    """Information extracted from a JWT.

    TODO: Add fields:
    - header: dict
    - claims: dict
    - algorithm: str
    - token_type: str
    - subject: str | None
    - issuer: str | None
    - audience: str | list[str] | None
    - expires_at: datetime | None
    - issued_at: datetime | None
    - is_expired: bool
    - expires_in_seconds: int | None
    """

    header: dict[str, Any]
    claims: dict[str, Any]

    @property
    def algorithm(self) -> str:
        """Get the signing algorithm."""
        # TODO: Extract from header
        raise NotImplementedError("Implement algorithm property")

    @property
    def token_type(self) -> str:
        """Get the token type."""
        # TODO: Extract from header
        raise NotImplementedError("Implement token_type property")

    @property
    def subject(self) -> str | None:
        """Get the subject claim."""
        # TODO: Extract from claims
        raise NotImplementedError("Implement subject property")

    @property
    def issuer(self) -> str | None:
        """Get the issuer claim."""
        # TODO: Extract from claims
        raise NotImplementedError("Implement issuer property")

    @property
    def expires_at(self) -> datetime | None:
        """Get expiration as datetime."""
        # TODO: Convert exp claim to datetime
        raise NotImplementedError("Implement expires_at property")

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        # TODO: Compare expires_at with current time
        raise NotImplementedError("Implement is_expired property")

    @property
    def expires_in_seconds(self) -> int | None:
        """Get seconds until expiration (negative if expired)."""
        # TODO: Calculate time difference
        raise NotImplementedError("Implement expires_in_seconds property")


class JWTDecoder:
    """Decodes JWTs without signature verification.

    WARNING: This is for debugging only. Never trust decoded
    data without verification in production!

    TODO: Implement:
    - decode(token: str) -> TokenInfo
    - _decode_part(part: str) -> dict
    - _add_base64_padding(data: str) -> str
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
        # TODO: Implement decoding
        # 1. Split token by '.'
        # 2. Decode header (first part)
        # 3. Decode payload (second part)
        # 4. Return TokenInfo
        raise NotImplementedError("Implement decode")

    def _decode_part(self, part: str) -> dict[str, Any]:
        """Decode a base64url-encoded JWT part.

        Args:
            part: The base64url-encoded string

        Returns:
            Decoded JSON as dict
        """
        # TODO: Implement base64 decoding
        # Hint: Add padding, then decode, then parse JSON
        raise NotImplementedError("Implement _decode_part")

    def _add_base64_padding(self, data: str) -> str:
        """Add padding to base64 string if needed.

        Args:
            data: The base64 string

        Returns:
            Padded string
        """
        # TODO: Add = padding to make length multiple of 4
        raise NotImplementedError("Implement _add_base64_padding")

    def format_info(self, info: TokenInfo) -> str:
        """Format token info for display.

        Args:
            info: The TokenInfo to format

        Returns:
            Human-readable string
        """
        # TODO: Format the info nicely
        raise NotImplementedError("Implement format_info")


def main() -> None:
    """Test your implementation."""
    print("Exercise 1: JWT Decoder")
    print("See the solution in solutions/solution_1.py")

    # Uncomment to test your implementation:
    #
    # import jwt
    # import secrets
    # from datetime import timedelta
    #
    # secret = secrets.token_urlsafe(32)
    # now = datetime.now(timezone.utc)
    #
    # # Create a test token
    # payload = {
    #     "sub": "user123",
    #     "name": "John Doe",
    #     "email": "john@example.com",
    #     "roles": ["user", "editor"],
    #     "iat": now,
    #     "exp": now + timedelta(hours=1),
    #     "iss": "https://auth.example.com",
    #     "aud": "my-api",
    # }
    # token = jwt.encode(payload, secret, algorithm="HS256")
    #
    # # Decode it
    # decoder = JWTDecoder()
    # info = decoder.decode(token)
    #
    # print(f"Algorithm: {info.algorithm}")
    # print(f"Subject: {info.subject}")
    # print(f"Issuer: {info.issuer}")
    # print(f"Expires at: {info.expires_at}")
    # print(f"Is expired: {info.is_expired}")
    # print(f"Expires in: {info.expires_in_seconds} seconds")
    #
    # print("\nFormatted:")
    # print(decoder.format_info(info))


if __name__ == "__main__":
    main()

"""Solution 2: Extract and Validate ID Token Claims"""

from dataclasses import dataclass
from typing import Any


@dataclass
class UserClaims:
    """Validated user claims from ID token."""

    subject: str
    issuer: str
    audience: str
    email: str | None
    name: str | None


REQUIRED_CLAIMS = ["sub", "iss", "aud"]


def extract_claims(payload: dict[str, Any]) -> UserClaims:
    """Extract and validate claims from ID token payload.

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        UserClaims with extracted information

    Raises:
        ValueError: If required claims are missing
    """
    # Check required claims
    missing = [claim for claim in REQUIRED_CLAIMS if claim not in payload]
    if missing:
        raise ValueError(f"Missing required claims: {', '.join(missing)}")

    # Handle audience - can be string or list
    aud = payload["aud"]
    if isinstance(aud, list):
        aud = aud[0]  # Use first audience if multiple

    return UserClaims(
        subject=payload["sub"],
        issuer=payload["iss"],
        audience=aud,
        email=payload.get("email"),
        name=payload.get("name"),
    )


if __name__ == "__main__":
    # Valid payload
    valid_payload = {
        "sub": "user-123",
        "iss": "https://auth.example.com",
        "aud": "client-456",
        "exp": 1234567890,
        "iat": 1234567800,
        "email": "user@example.com",
        "name": "Test User",
    }

    claims = extract_claims(valid_payload)
    assert claims.subject == "user-123"
    assert claims.issuer == "https://auth.example.com"
    assert claims.email == "user@example.com"
    print("Valid payload test passed!")

    # Missing required claim
    invalid_payload = {"email": "user@example.com"}
    try:
        extract_claims(invalid_payload)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"Caught expected error: {e}")
        print("Missing claim test passed!")

    # Payload with list audience
    list_aud_payload = {
        "sub": "user-123",
        "iss": "https://auth.example.com",
        "aud": ["client-456", "client-789"],
    }
    claims = extract_claims(list_aud_payload)
    assert claims.audience == "client-456"
    print("List audience test passed!")

    print("All tests passed!")

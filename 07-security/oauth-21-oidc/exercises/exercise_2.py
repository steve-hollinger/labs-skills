"""Exercise 2: Extract and Validate ID Token Claims

Your task: Implement a function that extracts standard OIDC claims
from a decoded ID token payload and validates required fields.

Requirements:
1. Extract standard claims: sub, iss, aud, exp, iat, email, name
2. Validate that all required claims are present
3. Return a UserClaims dataclass or raise ValueError if invalid
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class UserClaims:
    """Validated user claims from ID token."""

    subject: str  # sub claim
    issuer: str  # iss claim
    audience: str  # aud claim
    email: str | None
    name: str | None


def extract_claims(payload: dict[str, Any]) -> UserClaims:
    """Extract and validate claims from ID token payload.

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        UserClaims with extracted information

    Raises:
        ValueError: If required claims are missing

    TODO: Implement this function
    """
    # Your implementation here
    pass


# Test your implementation
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
    except ValueError:
        print("Missing claim test passed!")

    print("All tests passed!")

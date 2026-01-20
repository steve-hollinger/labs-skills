"""Example 1: Basic JWT Validation with HS256.

This example demonstrates fundamental JWT operations:
- Creating JWTs with HS256 algorithm
- Validating tokens and handling errors
- Working with standard claims
- Setting expiration and other time-based claims

Run with: make example-1
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import jwt

from jwt_validation import (
    InvalidClaimsError,
    TokenConfig,
    TokenExpiredError,
    TokenValidationError,
    TokenValidator,
    get_claim,
    get_expiration,
    has_role,
    is_expired,
)


def main() -> None:
    """Demonstrate basic JWT validation."""
    print("=" * 60)
    print("Example 1: Basic JWT Validation with HS256")
    print("=" * 60)

    # Generate a secure secret
    secret = secrets.token_urlsafe(32)
    print(f"\n1. Generated Secret: {secret[:20]}...")

    # 1. Create a simple token
    print("\n2. Creating a JWT")
    print("-" * 40)

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
    print(f"Token: {token[:50]}...")
    print(f"Token length: {len(token)} characters")

    # 2. Decode and inspect (without validation)
    print("\n3. Token Structure (decoded)")
    print("-" * 40)

    header = jwt.get_unverified_header(token)
    print(f"Header: {header}")

    # Safe to decode for inspection
    decoded = jwt.decode(token, options={"verify_signature": False})
    print(f"Payload claims:")
    for key, value in decoded.items():
        if key in ("iat", "exp", "nbf"):
            dt = datetime.fromtimestamp(value, tz=timezone.utc)
            print(f"  {key}: {value} ({dt.isoformat()})")
        else:
            print(f"  {key}: {value}")

    # 3. Validate with TokenValidator
    print("\n4. Validating Token")
    print("-" * 40)

    config = TokenConfig(
        secret=secret,
        algorithms=["HS256"],
        issuer="https://auth.example.com",
        audience="my-api",
        required_claims=["sub", "exp"],
    )
    validator = TokenValidator(config)

    try:
        validated_payload = validator.validate(token)
        print("Token is valid!")
        print(f"Subject: {validated_payload['sub']}")
        print(f"Name: {validated_payload['name']}")
    except TokenValidationError as e:
        print(f"Validation failed: {e}")

    # 4. Working with claims
    print("\n5. Working with Claims")
    print("-" * 40)

    print(f"Subject: {get_claim(validated_payload, 'sub')}")
    print(f"Email: {get_claim(validated_payload, 'email')}")
    print(f"Missing claim: {get_claim(validated_payload, 'phone', 'N/A')}")

    print(f"\nHas 'user' role: {has_role(validated_payload, 'user')}")
    print(f"Has 'admin' role: {has_role(validated_payload, 'admin')}")

    exp_time = get_expiration(validated_payload)
    print(f"\nExpires at: {exp_time}")
    print(f"Is expired: {is_expired(validated_payload)}")

    # 5. Error handling scenarios
    print("\n6. Error Handling Scenarios")
    print("-" * 40)

    # Wrong secret
    print("\na) Wrong secret:")
    try:
        wrong_config = TokenConfig(secret="wrong-secret", algorithms=["HS256"])
        wrong_validator = TokenValidator(wrong_config)
        wrong_validator.validate(token)
    except TokenValidationError as e:
        print(f"   Error: {e}")

    # Wrong issuer
    print("\nb) Wrong issuer:")
    try:
        issuer_config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            issuer="https://wrong-issuer.com",
        )
        issuer_validator = TokenValidator(issuer_config)
        issuer_validator.validate(token)
    except InvalidClaimsError as e:
        print(f"   Error: {e}")

    # Wrong audience
    print("\nc) Wrong audience:")
    try:
        aud_config = TokenConfig(
            secret=secret,
            algorithms=["HS256"],
            audience="wrong-api",
        )
        aud_validator = TokenValidator(aud_config)
        aud_validator.validate(token)
    except InvalidClaimsError as e:
        print(f"   Error: {e}")

    # Expired token
    print("\nd) Expired token:")
    expired_payload = {
        **payload,
        "exp": now - timedelta(hours=1),  # Already expired
    }
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")

    try:
        validator.validate(expired_token)
    except TokenExpiredError as e:
        print(f"   Error: {e}")

    # Missing required claim
    print("\ne) Missing required claim:")
    minimal_payload = {"name": "John"}  # Missing 'sub' and 'exp'
    minimal_token = jwt.encode(minimal_payload, secret, algorithm="HS256")

    try:
        validator.validate(minimal_token)
    except InvalidClaimsError as e:
        print(f"   Error: {e}")

    # 7. Algorithm mismatch (security!)
    print("\n7. Algorithm Mismatch (Security Check)")
    print("-" * 40)

    # This demonstrates why specifying algorithms is critical
    print("Always specify allowed algorithms to prevent algorithm confusion attacks!")
    print("Example: algorithms=['HS256'] - only accept HS256")

    print("\n" + "=" * 60)
    print("Example 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

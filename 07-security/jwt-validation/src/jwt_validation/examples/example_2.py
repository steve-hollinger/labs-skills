"""Example 2: RS256 with JWKS.

This example demonstrates asymmetric key JWT operations:
- Generating RSA key pairs
- Creating tokens with RS256
- Validating with public keys
- Working with JWKS format

Run with: make example-2
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from jwt_validation import (
    TokenConfig,
    TokenValidator,
    generate_rsa_keypair,
    get_private_key_pem,
    get_public_key_pem,
)
from jwt_validation.keys import LocalJWKS


def main() -> None:
    """Demonstrate RS256 JWT validation."""
    print("=" * 60)
    print("Example 2: RS256 with JWKS")
    print("=" * 60)

    # 1. Generate RSA key pair
    print("\n1. Generating RSA Key Pair")
    print("-" * 40)

    private_key, public_key = generate_rsa_keypair(key_size=2048)
    print("Generated 2048-bit RSA key pair")

    private_pem = get_private_key_pem(private_key)
    public_pem = get_public_key_pem(public_key)

    print(f"\nPrivate key (first 100 chars):")
    print(private_pem.decode()[:100] + "...")

    print(f"\nPublic key (first 100 chars):")
    print(public_pem.decode()[:100] + "...")

    # 2. Create a token with RS256
    print("\n2. Creating JWT with RS256")
    print("-" * 40)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user456",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "roles": ["admin", "user"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": "https://auth.example.com",
        "aud": "my-api",
    }

    # Sign with private key
    token = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": "key-1"},  # Key ID for JWKS
    )

    print(f"Token: {token[:60]}...")
    print(f"Token length: {len(token)} characters")

    # Inspect header
    header = jwt.get_unverified_header(token)
    print(f"\nHeader: {header}")

    # 3. Validate with public key
    print("\n3. Validating with Public Key")
    print("-" * 40)

    config = TokenConfig(
        secret=public_key,  # Use public key for RS256
        algorithms=["RS256"],
        issuer="https://auth.example.com",
        audience="my-api",
    )
    validator = TokenValidator(config)

    validated = validator.validate(token)
    print("Token is valid!")
    print(f"Subject: {validated['sub']}")
    print(f"Roles: {validated['roles']}")

    # 4. HS256 vs RS256 comparison
    print("\n4. HS256 vs RS256 Comparison")
    print("-" * 40)

    import secrets
    hs256_secret = secrets.token_urlsafe(32)

    # Create same payload with both algorithms
    hs256_token = jwt.encode(payload, hs256_secret, algorithm="HS256")
    rs256_token = token

    print(f"HS256 token length: {len(hs256_token)} chars")
    print(f"RS256 token length: {len(rs256_token)} chars")
    print("\nRS256 tokens are larger due to RSA signature")

    print("\nKey differences:")
    print("  HS256: Same secret for signing and verification")
    print("  RS256: Private key signs, public key verifies")
    print("\n  Use HS256 for: Internal services, simple setups")
    print("  Use RS256 for: Public APIs, OIDC, distributed systems")

    # 5. Working with JWKS
    print("\n5. Working with JWKS")
    print("-" * 40)

    # Create a local JWKS for demonstration
    jwks = LocalJWKS(key_id="test-key-2024")

    print("Created local JWKS provider")
    print(f"\nJWKS JSON (formatted):")

    import json
    jwks_data = jwks.get_jwks()
    print(json.dumps(jwks_data, indent=2))

    # Create and validate a token using JWKS
    print("\n6. Signing and Verifying with JWKS")
    print("-" * 40)

    jwks_payload = {
        "sub": "user789",
        "name": "Bob Wilson",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }

    jwks_token = jwks.sign_token(jwks_payload)
    print(f"Signed token with kid: {jwks.key_id}")

    # Verify the token
    verified = jwks.verify_token(jwks_token)
    print(f"Verified! Subject: {verified['sub']}")

    # Check the kid in header
    header = jwt.get_unverified_header(jwks_token)
    print(f"Token header kid: {header.get('kid')}")

    # 7. Why JWKS matters
    print("\n7. Why JWKS Matters")
    print("-" * 40)
    print("""
JWKS (JSON Web Key Sets) enables:

1. Key Rotation: Update signing keys without code changes
   - Add new key to JWKS
   - Start signing with new key
   - Remove old key after tokens expire

2. Public Key Distribution: Verifiers fetch keys automatically
   - No need to share secrets
   - Standard endpoint: /.well-known/jwks.json

3. Multiple Keys: Support different keys for different purposes
   - Each key has a unique 'kid' (key ID)
   - Tokens include 'kid' in header
   - Verifier selects correct key automatically

Example JWKS endpoint flow:
1. Client receives JWT with kid="key-2024"
2. Client fetches https://auth.example.com/.well-known/jwks.json
3. Client finds key with matching kid
4. Client verifies signature with that key
""")

    print("=" * 60)
    print("Example 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

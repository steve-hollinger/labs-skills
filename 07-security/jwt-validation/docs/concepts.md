# Core Concepts

## Overview

JSON Web Tokens (JWTs) are a standard for securely transmitting claims between parties. This document covers the core concepts for understanding and validating JWTs.

## Concept 1: JWT Structure

### What It Is

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Metadata about the token (algorithm, type)
2. **Payload**: The claims (statements about the subject)
3. **Signature**: Cryptographic verification of integrity

Each part is Base64URL encoded.

### Why It Matters

Understanding the structure helps you:
- Debug token issues
- Implement proper validation
- Choose appropriate algorithms
- Understand security implications

### How It Works

```python
import base64
import json

def decode_jwt_parts(token: str) -> tuple[dict, dict, bytes]:
    """Decode JWT into its three parts."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")

    # Add padding for base64 decoding
    def decode_part(part: str) -> bytes:
        padding = 4 - len(part) % 4
        return base64.urlsafe_b64decode(part + "=" * padding)

    header = json.loads(decode_part(parts[0]))
    payload = json.loads(decode_part(parts[1]))
    signature = decode_part(parts[2])

    return header, payload, signature


# Example token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

header, payload, sig = decode_jwt_parts(token)
print(f"Header: {header}")    # {'alg': 'HS256', 'typ': 'JWT'}
print(f"Payload: {payload}")  # {'sub': '1234567890', 'name': 'John'}
```

## Concept 2: Claims

### What It Is

Claims are statements about an entity (typically the user) and additional metadata. There are three types:

1. **Registered Claims**: Standardized claims defined in RFC 7519
2. **Public Claims**: Custom claims that should be collision-resistant
3. **Private Claims**: Custom claims for specific applications

### Why It Matters

Claims carry the actual information in a JWT:
- User identity (`sub`)
- Permissions and roles
- Token validity period (`exp`, `nbf`)
- Token context (`iss`, `aud`)

### Standard Registered Claims

| Claim | Name | Description | Example |
|-------|------|-------------|---------|
| `iss` | Issuer | Who created the token | `"https://auth.example.com"` |
| `sub` | Subject | Who the token is about | `"user123"` |
| `aud` | Audience | Who the token is for | `["api.example.com"]` |
| `exp` | Expiration | When the token expires | `1704067200` (Unix timestamp) |
| `nbf` | Not Before | When the token becomes valid | `1704063600` |
| `iat` | Issued At | When the token was created | `1704063600` |
| `jti` | JWT ID | Unique identifier for the token | `"abc-123-xyz"` |

### How It Works

```python
import jwt
from datetime import datetime, timedelta, timezone

def create_token_with_claims(
    user_id: str,
    secret: str,
    expires_in: timedelta = timedelta(hours=1),
    roles: list[str] | None = None,
) -> str:
    """Create a JWT with standard and custom claims."""
    now = datetime.now(timezone.utc)

    payload = {
        # Registered claims
        "iss": "https://myapp.example.com",
        "sub": user_id,
        "aud": "myapp-api",
        "exp": now + expires_in,
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),

        # Custom claims
        "roles": roles or [],
        "email_verified": True,
    }

    return jwt.encode(payload, secret, algorithm="HS256")
```

## Concept 3: Signature Algorithms

### What It Is

JWTs can be signed using different algorithms:

**Symmetric (HMAC)**:
- HS256, HS384, HS512
- Same secret for signing and verification
- Simpler but requires secure secret distribution

**Asymmetric (RSA/ECDSA)**:
- RS256, RS384, RS512 (RSA)
- ES256, ES384, ES512 (ECDSA)
- Private key for signing, public key for verification
- Better for distributed systems

### Why It Matters

Choosing the right algorithm affects:
- Security model (who can verify vs sign)
- Key management complexity
- Performance characteristics
- Interoperability with other systems

### How It Works

```python
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# HS256 - Symmetric
hs256_secret = "your-256-bit-secret"
token_hs256 = jwt.encode(payload, hs256_secret, algorithm="HS256")
decoded_hs256 = jwt.decode(token_hs256, hs256_secret, algorithms=["HS256"])

# RS256 - Asymmetric
# Generate key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Sign with private key
token_rs256 = jwt.encode(payload, private_key, algorithm="RS256")

# Verify with public key
decoded_rs256 = jwt.decode(token_rs256, public_key, algorithms=["RS256"])
```

## Concept 4: JWKS (JSON Web Key Sets)

### What It Is

JWKS is a standard format for publishing public keys used to verify JWTs. It's commonly used with RS256 and OIDC providers.

### Why It Matters

- Allows key rotation without code changes
- Enables token verification without shared secrets
- Standard format supported by major auth providers

### How It Works

JWKS endpoint returns keys in this format:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "key-id-1",
      "use": "sig",
      "alg": "RS256",
      "n": "base64url-encoded-modulus",
      "e": "AQAB"
    }
  ]
}
```

```python
from jwt import PyJWKClient

# Create client pointing to JWKS endpoint
jwks_client = PyJWKClient(
    "https://auth.example.com/.well-known/jwks.json",
    cache_jwk_set=True,
    lifespan=300  # Cache for 5 minutes
)

def validate_with_jwks(token: str, audience: str) -> dict:
    """Validate a JWT using JWKS."""
    # Get the signing key from the token's header
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # Decode and validate
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=audience
    )
```

## Summary

Key takeaways:

1. **Understand the structure**: Header.Payload.Signature
2. **Validate all relevant claims**: exp, iss, aud, sub at minimum
3. **Always specify algorithms**: Prevent algorithm confusion attacks
4. **Choose appropriate algorithm**: HS256 for simple cases, RS256 for distributed systems
5. **Use JWKS for public key distribution**: Enables key rotation and standardization

# JWT Validation

Learn how to validate JSON Web Tokens (JWTs) securely in Python applications. This skill covers token structure, claims validation, signature verification, and best practices for JWT authentication.

## Learning Objectives

After completing this skill, you will be able to:
- Understand JWT structure (header, payload, signature)
- Validate JWTs using PyJWT library
- Implement RS256 and HS256 signature verification
- Handle token expiration and claims validation
- Build secure authentication middleware

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of HTTP authentication (helpful)

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### What is a JWT?

A JSON Web Token is a compact, URL-safe means of representing claims between two parties. JWTs are commonly used for:
- API authentication
- Single Sign-On (SSO)
- Information exchange

A JWT consists of three parts separated by dots:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
|_______________________________|________________________|_______________________________|
            Header                       Payload                    Signature
```

### Token Structure

**Header**: Contains the algorithm and token type
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**: Contains the claims (statements about the user)
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}
```

**Signature**: Verifies the token hasn't been tampered with
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

### Validation in Python

```python
import jwt

# HS256 (symmetric) validation
try:
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        options={"require": ["exp", "sub"]}
    )
    print(f"Valid token for user: {payload['sub']}")
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError as e:
    print(f"Invalid token: {e}")
```

### RS256 vs HS256

| Algorithm | Type | Key | Use Case |
|-----------|------|-----|----------|
| HS256 | Symmetric | Shared secret | Internal services |
| RS256 | Asymmetric | Public/Private key pair | Public APIs, OIDC |

```python
# RS256 (asymmetric) validation
from jwt import PyJWKClient

jwks_client = PyJWKClient("https://auth.example.com/.well-known/jwks.json")
signing_key = jwks_client.get_signing_key_from_jwt(token)

payload = jwt.decode(
    token,
    signing_key.key,
    algorithms=["RS256"],
    audience="your-api"
)
```

## Examples

### Example 1: Basic JWT Validation

Create and validate JWTs with HS256 algorithm.

```bash
make example-1
```

### Example 2: RS256 with JWKS

Validate JWTs signed with RSA keys from a JWKS endpoint.

```bash
make example-2
```

### Example 3: FastAPI Authentication Middleware

Build a complete JWT authentication system for FastAPI.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement a JWT decoder that extracts claims without validation
2. **Exercise 2**: Build a custom claims validator with role-based access
3. **Exercise 3**: Create a token refresh mechanism with rotation

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Verifying the Signature
Never decode without verification in production:
```python
# DANGEROUS - never do this in production
payload = jwt.decode(token, options={"verify_signature": False})

# SAFE - always verify
payload = jwt.decode(token, secret, algorithms=["HS256"])
```

### Algorithm Confusion Attack
Always specify allowed algorithms:
```python
# VULNERABLE - accepts any algorithm
payload = jwt.decode(token, secret)

# SAFE - explicitly allow only expected algorithms
payload = jwt.decode(token, secret, algorithms=["RS256"])
```

### Not Validating Claims
Always validate critical claims:
```python
# Require specific claims
payload = jwt.decode(
    token,
    secret,
    algorithms=["HS256"],
    audience="your-api",
    issuer="your-auth-server",
    options={"require": ["exp", "sub", "aud", "iss"]}
)
```

### Using Weak Secrets
Use strong, randomly generated secrets:
```python
import secrets

# Bad - predictable secret
secret = "password123"

# Good - cryptographically secure
secret = secrets.token_urlsafe(32)
```

## Standard Claims

| Claim | Description | Example |
|-------|-------------|---------|
| `iss` | Issuer | `"https://auth.example.com"` |
| `sub` | Subject (user ID) | `"user123"` |
| `aud` | Audience | `"your-api"` |
| `exp` | Expiration time | `1516242622` |
| `nbf` | Not before | `1516239022` |
| `iat` | Issued at | `1516239022` |
| `jti` | JWT ID (unique identifier) | `"abc123"` |

## Further Reading

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT specification
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- Related skills in this repository:
  - [OAuth 2.1/OIDC](../oauth-21-oidc/)
  - [API Key Auth](../api-key-auth/)

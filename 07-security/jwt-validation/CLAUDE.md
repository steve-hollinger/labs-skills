# CLAUDE.md - JWT Validation

This skill teaches JWT token validation using Python's PyJWT library, covering token structure, claims validation, and signature verification.

## Key Concepts

- **JWT Structure**: Three parts (header.payload.signature) encoded in Base64URL
- **Claims Validation**: Verifying standard and custom claims (exp, iss, aud, sub)
- **Signature Algorithms**: HS256 (symmetric) vs RS256 (asymmetric)
- **JWKS**: JSON Web Key Sets for public key distribution

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic JWT validation
make example-2  # RS256 with JWKS
make example-3  # FastAPI middleware
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
jwt-validation/
├── src/jwt_validation/
│   ├── __init__.py
│   ├── validator.py       # Core validation logic
│   ├── claims.py          # Claims validation utilities
│   ├── keys.py            # Key management (JWKS, etc.)
│   └── examples/
│       ├── example_1.py   # Basic HS256 validation
│       ├── example_2.py   # RS256 with JWKS
│       └── example_3.py   # FastAPI middleware
├── exercises/
│   ├── exercise_1.py      # JWT decoder
│   ├── exercise_2.py      # Custom claims validator
│   ├── exercise_3.py      # Token refresh
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic JWT Validation
```python
import jwt

def validate_token(token: str, secret: str) -> dict:
    """Validate a JWT and return the payload."""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {e}")
```

### Pattern 2: RS256 with JWKS
```python
from jwt import PyJWKClient

class JWKSValidator:
    def __init__(self, jwks_url: str):
        self.jwks_client = PyJWKClient(jwks_url, cache_jwk_set=True)

    def validate(self, token: str, audience: str) -> dict:
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience
        )
```

### Pattern 3: FastAPI Dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = validate_token(credentials.credentials)
        return payload
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

## Common Mistakes

1. **Not specifying algorithms**
   - Why: Algorithm confusion attacks can bypass signature verification
   - Fix: Always specify `algorithms=["RS256"]` or `algorithms=["HS256"]`

2. **Accepting expired tokens**
   - Why: Default behavior may not enforce expiration
   - Fix: Include `exp` in required claims with `options={"require": ["exp"]}`

3. **Using weak secrets**
   - Why: Weak secrets can be brute-forced
   - Fix: Use `secrets.token_urlsafe(32)` for HS256 secrets

4. **Not validating audience**
   - Why: Tokens for other services could be used
   - Fix: Always set `audience` parameter when decoding

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "Should I use HS256 or RS256?"
- HS256: Simpler, good for internal services where secret can be shared securely
- RS256: Better for public APIs, OIDC, when verifier shouldn't know the signing key

### "How do I handle token refresh?"
See example_3.py for refresh token patterns. Best practices:
- Short-lived access tokens (15 min)
- Long-lived refresh tokens (days/weeks)
- Rotate refresh tokens on use

### "What claims should I validate?"
Always validate:
- `exp`: Expiration time
- `iss`: Issuer (who created the token)
- `aud`: Audience (who the token is for)
- `sub`: Subject (who the token is about)

## Testing Notes

- Tests use locally generated keys (no network)
- Tests cover both HS256 and RS256
- Tests verify expiration and claims validation
- Mock JWKS endpoint for RS256 tests

## Dependencies

Key dependencies in pyproject.toml:
- PyJWT[crypto]: JWT encoding/decoding with RSA support
- cryptography: For RSA key generation
- httpx: For JWKS fetching (optional)

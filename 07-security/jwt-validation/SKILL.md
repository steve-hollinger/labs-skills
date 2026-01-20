---
name: validating-jwt-tokens
description: This skill teaches JWT token validation using Python's PyJWT library, covering token structure, claims validation, and signature verification. Use when implementing authentication or verifying tokens.
---

# Jwt Validation

## Quick Start
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
    # ... see docs/patterns.md for more
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic JWT validation
make example-2  # RS256 with JWKS
make example-3  # FastAPI middleware
make test       # Run pytest
```

## Key Points
- JWT Structure
- Claims Validation
- Signature Algorithms

## Common Mistakes
1. **Not specifying algorithms** - Always specify `algorithms=["RS256"]` or `algorithms=["HS256"]`
2. **Accepting expired tokens** - Include `exp` in required claims with `options={"require": ["exp"]}`
3. **Using weak secrets** - Use `secrets.token_urlsafe(32)` for HS256 secrets

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
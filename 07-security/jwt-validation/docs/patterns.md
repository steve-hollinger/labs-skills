# Common Patterns

## Overview

This document covers common patterns and best practices for JWT validation in Python applications.

## Pattern 1: Secure Token Validator Class

### When to Use

When you need a reusable, configurable JWT validator with proper error handling.

### Implementation

```python
from dataclasses import dataclass
from typing import Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError


class TokenValidationError(Exception):
    """Base exception for token validation errors."""
    pass


class TokenExpiredError(TokenValidationError):
    """Token has expired."""
    pass


class InvalidSignatureError(TokenValidationError):
    """Token signature is invalid."""
    pass


class InvalidClaimsError(TokenValidationError):
    """Token claims are invalid."""
    pass


@dataclass
class TokenConfig:
    """Configuration for token validation."""
    secret: str
    algorithms: list[str]
    issuer: str | None = None
    audience: str | None = None
    required_claims: list[str] | None = None
    leeway: int = 0  # Seconds of leeway for exp validation


class TokenValidator:
    """Validates JWTs with configurable options."""

    def __init__(self, config: TokenConfig):
        self.config = config

    def validate(self, token: str) -> dict[str, Any]:
        """Validate a JWT and return the payload.

        Args:
            token: The JWT string

        Returns:
            The decoded payload

        Raises:
            TokenExpiredError: Token has expired
            InvalidSignatureError: Signature verification failed
            InvalidClaimsError: Required claims missing or invalid
        """
        options = {}
        if self.config.required_claims:
            options["require"] = self.config.required_claims

        try:
            return jwt.decode(
                token,
                self.config.secret,
                algorithms=self.config.algorithms,
                issuer=self.config.issuer,
                audience=self.config.audience,
                options=options,
                leeway=self.config.leeway,
            )
        except ExpiredSignatureError as e:
            raise TokenExpiredError("Token has expired") from e
        except jwt.InvalidSignatureError as e:
            raise InvalidSignatureError("Invalid token signature") from e
        except jwt.InvalidIssuerError as e:
            raise InvalidClaimsError(f"Invalid issuer: {e}") from e
        except jwt.InvalidAudienceError as e:
            raise InvalidClaimsError(f"Invalid audience: {e}") from e
        except jwt.MissingRequiredClaimError as e:
            raise InvalidClaimsError(f"Missing required claim: {e}") from e
        except InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {e}") from e
```

### Example

```python
config = TokenConfig(
    secret="your-secret-key",
    algorithms=["HS256"],
    issuer="https://auth.example.com",
    audience="my-api",
    required_claims=["sub", "exp"],
    leeway=30,  # 30 seconds leeway
)

validator = TokenValidator(config)

try:
    payload = validator.validate(token)
    print(f"User: {payload['sub']}")
except TokenExpiredError:
    print("Please log in again")
except TokenValidationError as e:
    print(f"Authentication failed: {e}")
```

### Pitfalls to Avoid

- Don't catch all exceptions silently
- Don't use a generic algorithm list
- Don't skip issuer/audience validation in production

## Pattern 2: JWKS-Based Validator with Caching

### When to Use

When validating tokens from OIDC providers or external auth services using RS256.

### Implementation

```python
from functools import lru_cache
from jwt import PyJWKClient, PyJWKClientError
import jwt


class JWKSValidator:
    """Validates JWTs using a JWKS endpoint."""

    def __init__(
        self,
        jwks_url: str,
        audience: str,
        issuer: str | None = None,
        algorithms: list[str] | None = None,
        cache_keys: bool = True,
        cache_ttl: int = 300,
    ):
        self.audience = audience
        self.issuer = issuer
        self.algorithms = algorithms or ["RS256"]

        self.jwks_client = PyJWKClient(
            jwks_url,
            cache_jwk_set=cache_keys,
            lifespan=cache_ttl,
        )

    def validate(self, token: str) -> dict[str, Any]:
        """Validate a JWT using JWKS.

        Args:
            token: The JWT string

        Returns:
            The decoded payload

        Raises:
            TokenValidationError: If validation fails
        """
        try:
            # Get signing key from JWKS based on token's kid
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            return jwt.decode(
                token,
                signing_key.key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
            )
        except PyJWKClientError as e:
            raise TokenValidationError(f"Failed to fetch signing key: {e}") from e
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {e}") from e


# Usage with Auth0
auth0_validator = JWKSValidator(
    jwks_url="https://your-tenant.auth0.com/.well-known/jwks.json",
    audience="https://your-api.example.com",
    issuer="https://your-tenant.auth0.com/",
)
```

### Pitfalls to Avoid

- Don't disable key caching in production
- Don't forget to validate both audience and issuer
- Don't use HTTP (not HTTPS) for JWKS URLs

## Pattern 3: FastAPI Authentication Dependency

### When to Use

When building a FastAPI application that requires JWT authentication.

### Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated


security = HTTPBearer()


class AuthService:
    """Authentication service for FastAPI."""

    def __init__(self, validator: TokenValidator):
        self.validator = validator

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict[str, Any]:
        """Dependency that validates the token and returns the user."""
        try:
            return self.validator.validate(credentials.credentials)
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except TokenValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    def require_roles(self, required_roles: list[str]):
        """Create a dependency that requires specific roles."""
        async def check_roles(
            user: Annotated[dict, Depends(self.get_current_user)]
        ) -> dict[str, Any]:
            user_roles = user.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return user
        return check_roles


# Setup
validator = TokenValidator(TokenConfig(...))
auth = AuthService(validator)

# Usage in routes
@app.get("/users/me")
async def get_current_user(
    user: Annotated[dict, Depends(auth.get_current_user)]
):
    return {"user_id": user["sub"]}

@app.get("/admin/users")
async def list_users(
    user: Annotated[dict, Depends(auth.require_roles(["admin"]))]
):
    return {"users": [...]}
```

### Pitfalls to Avoid

- Don't forget WWW-Authenticate header in 401 responses
- Don't put sensitive data in error messages
- Don't use synchronous operations in async dependencies

## Pattern 4: Token Refresh with Rotation

### When to Use

When implementing a secure token refresh mechanism.

### Implementation

```python
from datetime import datetime, timedelta, timezone
import secrets


class TokenPair:
    """Manages access and refresh token pairs."""

    def __init__(self, secret: str, refresh_secret: str):
        self.access_secret = secret
        self.refresh_secret = refresh_secret
        self.access_ttl = timedelta(minutes=15)
        self.refresh_ttl = timedelta(days=7)
        # In production, use Redis or database
        self._revoked_tokens: set[str] = set()

    def create_tokens(self, user_id: str, roles: list[str]) -> dict[str, str]:
        """Create a new access/refresh token pair."""
        now = datetime.now(timezone.utc)
        jti = secrets.token_urlsafe(16)

        access_token = jwt.encode(
            {
                "sub": user_id,
                "roles": roles,
                "exp": now + self.access_ttl,
                "iat": now,
                "type": "access",
            },
            self.access_secret,
            algorithm="HS256",
        )

        refresh_token = jwt.encode(
            {
                "sub": user_id,
                "jti": jti,
                "exp": now + self.refresh_ttl,
                "iat": now,
                "type": "refresh",
            },
            self.refresh_secret,
            algorithm="HS256",
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(self.access_ttl.total_seconds()),
        }

    def refresh(self, refresh_token: str) -> dict[str, str]:
        """Use a refresh token to get new tokens.

        Implements refresh token rotation for security.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.refresh_secret,
                algorithms=["HS256"],
            )
        except jwt.InvalidTokenError as e:
            raise TokenValidationError(f"Invalid refresh token: {e}")

        if payload.get("type") != "refresh":
            raise TokenValidationError("Not a refresh token")

        jti = payload.get("jti")
        if jti in self._revoked_tokens:
            raise TokenValidationError("Refresh token has been revoked")

        # Revoke the used refresh token (rotation)
        self._revoked_tokens.add(jti)

        # Issue new token pair
        return self.create_tokens(
            payload["sub"],
            payload.get("roles", []),
        )

    def revoke_refresh_token(self, jti: str) -> None:
        """Revoke a refresh token."""
        self._revoked_tokens.add(jti)
```

### Pitfalls to Avoid

- Don't use the same secret for access and refresh tokens
- Don't forget to implement token revocation
- Don't store revoked tokens only in memory (use Redis/database)

## Anti-Patterns

### Anti-Pattern 1: Algorithm in Token

Never trust the algorithm specified in the token header.

```python
# DANGEROUS - trusts token's algorithm
header = jwt.get_unverified_header(token)
payload = jwt.decode(token, secret, algorithms=[header["alg"]])
```

### Better Approach

```python
# SAFE - specify allowed algorithms
payload = jwt.decode(token, secret, algorithms=["HS256"])
```

### Anti-Pattern 2: Decoding Without Verification

```python
# DANGEROUS - skips signature verification
payload = jwt.decode(token, options={"verify_signature": False})
```

### Better Approach

```python
# SAFE - always verify
payload = jwt.decode(token, secret, algorithms=["HS256"])
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Simple internal API | Secure Token Validator |
| Auth0/Okta/Azure AD | JWKS-Based Validator |
| FastAPI application | Authentication Dependency |
| Long-lived sessions | Token Refresh with Rotation |
| Microservices | JWKS with shared issuer |

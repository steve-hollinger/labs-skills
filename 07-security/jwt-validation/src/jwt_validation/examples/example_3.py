"""Example 3: FastAPI Authentication Middleware.

This example demonstrates a complete JWT authentication system:
- FastAPI dependency injection for auth
- Role-based access control
- Token refresh mechanism
- Protected endpoints

Run with: make example-3

Note: This example runs a demonstration without actually starting a server.
      See the patterns in docs/patterns.md for full FastAPI integration.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from jwt_validation import (
    TokenConfig,
    TokenExpiredError,
    TokenValidationError,
    TokenValidator,
    has_any_role,
    has_role,
)


# Simulated user database
USERS_DB = {
    "user123": {
        "id": "user123",
        "email": "john@example.com",
        "name": "John Doe",
        "roles": ["user"],
        "password_hash": "hashed_password_123",  # In reality, use bcrypt
    },
    "admin456": {
        "id": "admin456",
        "email": "admin@example.com",
        "name": "Admin User",
        "roles": ["admin", "user"],
        "password_hash": "hashed_password_456",
    },
}


@dataclass
class TokenPair:
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


class AuthService:
    """Authentication service for managing JWTs."""

    def __init__(
        self,
        secret: str,
        refresh_secret: str,
        issuer: str = "https://auth.example.com",
        audience: str = "my-api",
    ):
        self.secret = secret
        self.refresh_secret = refresh_secret
        self.issuer = issuer
        self.audience = audience

        # Access token: short-lived (15 min)
        self.access_token_ttl = timedelta(minutes=15)

        # Refresh token: longer-lived (7 days)
        self.refresh_token_ttl = timedelta(days=7)

        # Validator for access tokens
        self.validator = TokenValidator(
            TokenConfig(
                secret=secret,
                algorithms=["HS256"],
                issuer=issuer,
                audience=audience,
                required_claims=["sub", "exp", "type"],
            )
        )

        # Validator for refresh tokens
        self.refresh_validator = TokenValidator(
            TokenConfig(
                secret=refresh_secret,
                algorithms=["HS256"],
                issuer=issuer,
                required_claims=["sub", "exp", "jti", "type"],
            )
        )

        # Track revoked refresh tokens (in production, use Redis/database)
        self._revoked_tokens: set[str] = set()

    def create_tokens(self, user_id: str, roles: list[str]) -> TokenPair:
        """Create access and refresh token pair."""
        now = datetime.now(timezone.utc)
        jti = secrets.token_urlsafe(16)

        # Access token
        access_payload = {
            "sub": user_id,
            "roles": roles,
            "type": "access",
            "iat": now,
            "exp": now + self.access_token_ttl,
            "iss": self.issuer,
            "aud": self.audience,
        }
        access_token = jwt.encode(access_payload, self.secret, algorithm="HS256")

        # Refresh token
        refresh_payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": jti,
            "iat": now,
            "exp": now + self.refresh_token_ttl,
            "iss": self.issuer,
        }
        refresh_token = jwt.encode(
            refresh_payload, self.refresh_secret, algorithm="HS256"
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.access_token_ttl.total_seconds()),
        )

    def validate_access_token(self, token: str) -> dict[str, Any]:
        """Validate an access token."""
        payload = self.validator.validate(token)
        if payload.get("type") != "access":
            raise TokenValidationError("Not an access token")
        return payload

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Use a refresh token to get new tokens.

        Implements refresh token rotation for security.
        """
        payload = self.refresh_validator.validate(refresh_token)

        if payload.get("type") != "refresh":
            raise TokenValidationError("Not a refresh token")

        jti = payload.get("jti")
        if jti in self._revoked_tokens:
            raise TokenValidationError("Refresh token has been revoked")

        # Revoke the used refresh token (rotation)
        self._revoked_tokens.add(jti)

        # Get user to include current roles
        user = USERS_DB.get(payload["sub"])
        if not user:
            raise TokenValidationError("User not found")

        return self.create_tokens(user["id"], user["roles"])

    def revoke_refresh_token(self, jti: str) -> None:
        """Revoke a refresh token."""
        self._revoked_tokens.add(jti)


class AuthorizationError(Exception):
    """User is not authorized for this action."""

    pass


def require_auth(auth_service: AuthService, token: str) -> dict[str, Any]:
    """Dependency to require authentication."""
    try:
        return auth_service.validate_access_token(token)
    except TokenExpiredError:
        raise AuthorizationError("Token has expired. Please refresh or log in again.")
    except TokenValidationError as e:
        raise AuthorizationError(f"Invalid token: {e}")


def require_roles(
    user: dict[str, Any], required_roles: list[str], require_all: bool = False
) -> None:
    """Check if user has required roles."""
    if require_all:
        if not all(has_role(user, role) for role in required_roles):
            raise AuthorizationError(
                f"Missing required roles. Need all of: {required_roles}"
            )
    else:
        if not has_any_role(user, required_roles):
            raise AuthorizationError(
                f"Missing required role. Need one of: {required_roles}"
            )


def main() -> None:
    """Demonstrate FastAPI-style authentication."""
    print("=" * 60)
    print("Example 3: FastAPI Authentication Pattern")
    print("=" * 60)

    # Initialize auth service
    secret = secrets.token_urlsafe(32)
    refresh_secret = secrets.token_urlsafe(32)

    auth = AuthService(
        secret=secret,
        refresh_secret=refresh_secret,
    )

    # 1. User login (simulate)
    print("\n1. User Login")
    print("-" * 40)

    user = USERS_DB["user123"]
    tokens = auth.create_tokens(user["id"], user["roles"])

    print(f"User: {user['name']} ({user['email']})")
    print(f"Roles: {user['roles']}")
    print(f"Access token: {tokens.access_token[:50]}...")
    print(f"Refresh token: {tokens.refresh_token[:50]}...")
    print(f"Expires in: {tokens.expires_in} seconds")

    # 2. Access protected resource
    print("\n2. Accessing Protected Resource")
    print("-" * 40)

    # Simulate: GET /users/me
    try:
        current_user = require_auth(auth, tokens.access_token)
        print(f"GET /users/me")
        print(f"  Authenticated as: {current_user['sub']}")
        print(f"  User roles: {current_user['roles']}")
    except AuthorizationError as e:
        print(f"  Access denied: {e}")

    # 3. Role-based access
    print("\n3. Role-Based Access Control")
    print("-" * 40)

    # User trying to access admin endpoint
    print("\na) Regular user accessing admin endpoint:")
    try:
        current_user = require_auth(auth, tokens.access_token)
        require_roles(current_user, ["admin"])
        print("  Access granted to admin endpoint")
    except AuthorizationError as e:
        print(f"  Access denied: {e}")

    # Admin login
    print("\nb) Admin user accessing admin endpoint:")
    admin_user = USERS_DB["admin456"]
    admin_tokens = auth.create_tokens(admin_user["id"], admin_user["roles"])

    try:
        current_user = require_auth(auth, admin_tokens.access_token)
        require_roles(current_user, ["admin"])
        print(f"  Access granted! User: {current_user['sub']}")
    except AuthorizationError as e:
        print(f"  Access denied: {e}")

    # 4. Token refresh
    print("\n4. Token Refresh")
    print("-" * 40)

    print("Using refresh token to get new tokens...")
    new_tokens = auth.refresh_tokens(tokens.refresh_token)
    print(f"New access token: {new_tokens.access_token[:50]}...")
    print(f"New refresh token: {new_tokens.refresh_token[:50]}...")

    # Old refresh token should be revoked
    print("\nTrying to use old refresh token again:")
    try:
        auth.refresh_tokens(tokens.refresh_token)
        print("  Got new tokens (unexpected!)")
    except TokenValidationError as e:
        print(f"  Correctly rejected: {e}")

    # 5. New tokens work
    print("\n5. Using New Tokens")
    print("-" * 40)

    try:
        current_user = require_auth(auth, new_tokens.access_token)
        print(f"New access token works! User: {current_user['sub']}")
    except AuthorizationError as e:
        print(f"  Failed: {e}")

    # 6. FastAPI integration pattern
    print("\n6. FastAPI Integration Pattern")
    print("-" * 40)
    print("""
# In your FastAPI app:

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
auth_service = AuthService(secret, refresh_secret)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        return auth_service.validate_access_token(credentials.credentials)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Token expired")
    except TokenValidationError as e:
        raise HTTPException(status_code=401, detail=str(e))

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin required")
    return user

# Usage:
@app.get("/users/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"user_id": user["sub"]}

@app.get("/admin/stats")
async def get_stats(user: dict = Depends(require_admin)):
    return {"stats": "..."}
""")

    print("=" * 60)
    print("Example 3 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

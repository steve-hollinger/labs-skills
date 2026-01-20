"""Example 2: FastAPI Integration.

This example demonstrates:
- Creating a FastAPI app with API key auth
- Using dependencies for validation
- Proper error handling and response headers

Run with: make example-2

Note: This example demonstrates the pattern without running a server.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from api_key_auth import (
    APIKeyInfo,
    APIKeyValidator,
    KeyStore,
    RateLimitConfig,
    SlidingWindowRateLimiter,
    ValidationResult,
    generate_api_key,
)
from api_key_auth.storage import KeyTier


def create_demo_store() -> tuple[KeyStore, dict[str, str]]:
    """Create a demo key store with some test keys."""
    store = KeyStore()
    keys = {}

    # Create some test keys
    keys["user"] = generate_api_key("sk_live")
    store.store(
        key=keys["user"],
        name="User Key",
        owner_id="user_123",
        tier=KeyTier.BASIC,
        metadata={"scopes": ["read"]},
    )

    keys["admin"] = generate_api_key("sk_live")
    store.store(
        key=keys["admin"],
        name="Admin Key",
        owner_id="admin_456",
        tier=KeyTier.PRO,
        metadata={"scopes": ["read", "write", "admin"]},
    )

    return store, keys


def simulate_fastapi_request(
    validator: APIKeyValidator,
    rate_limiter: SlidingWindowRateLimiter | None,
    api_key: str | None,
    endpoint: str,
) -> dict[str, Any]:
    """Simulate a FastAPI request with API key validation.

    This simulates what the FastAPI dependency would do.
    """
    result: dict[str, Any] = {
        "endpoint": endpoint,
        "timestamp": datetime.utcnow().isoformat(),
        "headers": {},
    }

    # Step 1: Validate the API key
    if not api_key:
        result["status"] = 401
        result["body"] = {"detail": "API key is required"}
        result["headers"]["WWW-Authenticate"] = "ApiKey"
        return result

    response = validator.validate(api_key)

    if response.result == ValidationResult.INVALID:
        result["status"] = 401
        result["body"] = {"detail": response.message or "Invalid API key"}
        result["headers"]["WWW-Authenticate"] = "ApiKey"
        return result

    if response.result == ValidationResult.REVOKED:
        result["status"] = 401
        result["body"] = {"detail": "API key has been revoked"}
        return result

    if response.result == ValidationResult.EXPIRED:
        result["status"] = 401
        result["body"] = {"detail": "API key has expired"}
        return result

    # Step 2: Check rate limit
    if rate_limiter and response.key_info:
        rate_result = rate_limiter.check(response.key_info.id)

        result["headers"]["X-RateLimit-Limit"] = str(rate_result.limit)
        result["headers"]["X-RateLimit-Remaining"] = str(rate_result.remaining)
        result["headers"]["X-RateLimit-Reset"] = str(int(rate_result.reset_at))

        if not rate_result.allowed:
            result["status"] = 429
            result["body"] = {"detail": "Rate limit exceeded"}
            result["headers"]["Retry-After"] = str(int(rate_result.retry_after or 60))
            return result

    # Step 3: Success!
    result["status"] = 200
    result["body"] = {
        "message": f"Welcome, {response.key_info.name}!",
        "owner_id": response.key_info.owner_id,
        "tier": response.key_info.tier.value,
    }

    return result


def main() -> None:
    """Demonstrate FastAPI integration patterns."""
    print("=" * 60)
    print("Example 2: FastAPI Integration")
    print("=" * 60)

    # Create demo store and keys
    store, keys = create_demo_store()

    # Create validator and rate limiter
    validator = APIKeyValidator(store, required_prefix="sk_live")
    rate_limiter = SlidingWindowRateLimiter(RateLimitConfig(
        requests_per_minute=5,  # Low for demo
        requests_per_hour=100,
        requests_per_day=1000,
    ))

    # 1. Successful request
    print("\n1. Successful Request")
    print("-" * 40)

    result = simulate_fastapi_request(
        validator, rate_limiter,
        api_key=keys["user"],
        endpoint="/api/data"
    )

    print(f"Status: {result['status']}")
    print(f"Body: {result['body']}")
    print(f"Headers: {result['headers']}")

    # 2. Request without API key
    print("\n2. Request Without API Key")
    print("-" * 40)

    result = simulate_fastapi_request(
        validator, rate_limiter,
        api_key=None,
        endpoint="/api/data"
    )

    print(f"Status: {result['status']}")
    print(f"Body: {result['body']}")
    print(f"Headers: {result['headers']}")

    # 3. Request with invalid key
    print("\n3. Request With Invalid Key")
    print("-" * 40)

    result = simulate_fastapi_request(
        validator, rate_limiter,
        api_key="sk_example_FAKE",
        endpoint="/api/data"
    )

    print(f"Status: {result['status']}")
    print(f"Body: {result['body']}")

    # 4. Request with wrong prefix
    print("\n4. Request With Wrong Prefix")
    print("-" * 40)

    result = simulate_fastapi_request(
        validator, rate_limiter,
        api_key="pk_test_abc123xyz789def456",
        endpoint="/api/data"
    )

    print(f"Status: {result['status']}")
    print(f"Body: {result['body']}")

    # 5. Rate limiting demonstration
    print("\n5. Rate Limiting Demonstration")
    print("-" * 40)

    print(f"Making requests until rate limited (limit: 5/min)...")
    for i in range(7):
        result = simulate_fastapi_request(
            validator, rate_limiter,
            api_key=keys["admin"],
            endpoint="/api/data"
        )
        remaining = result["headers"].get("X-RateLimit-Remaining", "N/A")
        print(f"  Request {i+1}: Status {result['status']}, Remaining: {remaining}")
        if result["status"] == 429:
            print(f"  Retry-After: {result['headers'].get('Retry-After')} seconds")
            break

    # 6. Show FastAPI code pattern
    print("\n6. FastAPI Code Pattern")
    print("-" * 40)

    fastapi_code = '''
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from api_key_auth import APIKeyValidator, KeyStore, ValidationResult

app = FastAPI()
store = KeyStore()
validator = APIKeyValidator(store)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(
    api_key: str | None = Security(api_key_header)
) -> APIKeyInfo:
    """Dependency that validates API key."""
    response = validator.validate(api_key)

    if response.result != ValidationResult.VALID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.message or "Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return response.key_info

@app.get("/protected")
async def protected_endpoint(
    key_info: APIKeyInfo = Depends(get_api_key)
):
    """Endpoint that requires API key authentication."""
    return {
        "message": f"Hello, {key_info.name}!",
        "owner_id": key_info.owner_id,
    }

@app.get("/admin")
async def admin_endpoint(
    key_info: APIKeyInfo = Depends(get_api_key)
):
    """Endpoint that requires admin scope."""
    if "admin" not in key_info.metadata.get("scopes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin scope required"
        )
    return {"message": "Admin access granted"}
'''

    print(fastapi_code)

    print("\n" + "=" * 60)
    print("Example 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

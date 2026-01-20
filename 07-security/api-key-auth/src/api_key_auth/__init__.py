"""API Key Authentication skill module.

This module provides utilities for implementing API key authentication
in Python web applications.
"""

from api_key_auth.generator import (
    generate_api_key,
    get_key_prefix,
    validate_key_format,
)
from api_key_auth.storage import (
    APIKeyInfo,
    KeyStore,
    hash_key,
    verify_key,
)
from api_key_auth.validator import (
    APIKeyValidator,
    ValidationResult,
    ValidationResponse,
)
from api_key_auth.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    SlidingWindowRateLimiter,
)

__all__ = [
    # Generator
    "generate_api_key",
    "get_key_prefix",
    "validate_key_format",
    # Storage
    "APIKeyInfo",
    "KeyStore",
    "hash_key",
    "verify_key",
    # Validator
    "APIKeyValidator",
    "ValidationResult",
    "ValidationResponse",
    # Rate limiting
    "RateLimitConfig",
    "RateLimiter",
    "SlidingWindowRateLimiter",
]

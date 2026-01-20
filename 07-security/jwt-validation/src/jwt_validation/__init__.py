"""JWT Validation skill module.

This module provides utilities for validating JSON Web Tokens (JWTs)
with support for HS256 and RS256 algorithms.
"""

from jwt_validation.validator import (
    InvalidClaimsError,
    InvalidSignatureError,
    TokenConfig,
    TokenExpiredError,
    TokenValidationError,
    TokenValidator,
)
from jwt_validation.claims import (
    ClaimsValidator,
    validate_claims,
    get_claim,
    has_role,
)
from jwt_validation.keys import (
    JWKSValidator,
    generate_rsa_keypair,
    get_public_key_pem,
    get_private_key_pem,
)

__all__ = [
    # Validator
    "TokenValidator",
    "TokenConfig",
    "TokenValidationError",
    "TokenExpiredError",
    "InvalidSignatureError",
    "InvalidClaimsError",
    # Claims
    "ClaimsValidator",
    "validate_claims",
    "get_claim",
    "has_role",
    # Keys
    "JWKSValidator",
    "generate_rsa_keypair",
    "get_public_key_pem",
    "get_private_key_pem",
]

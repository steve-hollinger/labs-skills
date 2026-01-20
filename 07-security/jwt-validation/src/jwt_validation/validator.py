"""JWT validation utilities.

This module provides the core token validation functionality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError as JWTInvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
)


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
    """Token claims are invalid or missing."""

    pass


@dataclass
class TokenConfig:
    """Configuration for token validation.

    Attributes:
        secret: The secret key for HS256 or public key for RS256
        algorithms: List of allowed algorithms (e.g., ["HS256", "RS256"])
        issuer: Expected token issuer (iss claim)
        audience: Expected token audience (aud claim)
        required_claims: List of claims that must be present
        leeway: Seconds of leeway for expiration validation
        verify_signature: Whether to verify the signature (always True in production!)
        verify_exp: Whether to verify expiration
    """

    secret: str | bytes | Any
    algorithms: list[str] = field(default_factory=lambda: ["HS256"])
    issuer: str | None = None
    audience: str | list[str] | None = None
    required_claims: list[str] | None = None
    leeway: int = 0
    verify_signature: bool = True
    verify_exp: bool = True


class TokenValidator:
    """Validates JWTs with configurable options.

    Example:
        config = TokenConfig(
            secret="your-secret-key",
            algorithms=["HS256"],
            issuer="https://auth.example.com",
            audience="my-api",
            required_claims=["sub", "exp"]
        )
        validator = TokenValidator(config)
        payload = validator.validate(token)
    """

    def __init__(self, config: TokenConfig):
        """Initialize the validator.

        Args:
            config: Token validation configuration
        """
        self.config = config

    def validate(self, token: str) -> dict[str, Any]:
        """Validate a JWT and return the payload.

        Args:
            token: The JWT string to validate

        Returns:
            The decoded payload as a dictionary

        Raises:
            TokenExpiredError: If the token has expired
            InvalidSignatureError: If signature verification fails
            InvalidClaimsError: If claims validation fails
            TokenValidationError: For other validation errors
        """
        options: dict[str, Any] = {
            "verify_signature": self.config.verify_signature,
            "verify_exp": self.config.verify_exp,
        }

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
        except JWTInvalidSignatureError as e:
            raise InvalidSignatureError("Invalid token signature") from e
        except InvalidIssuerError as e:
            raise InvalidClaimsError(f"Invalid issuer: {e}") from e
        except InvalidAudienceError as e:
            raise InvalidClaimsError(f"Invalid audience: {e}") from e
        except MissingRequiredClaimError as e:
            raise InvalidClaimsError(f"Missing required claim: {e}") from e
        except DecodeError as e:
            raise TokenValidationError(f"Failed to decode token: {e}") from e
        except InvalidTokenError as e:
            raise TokenValidationError(f"Invalid token: {e}") from e

    def decode_header(self, token: str) -> dict[str, Any]:
        """Decode the token header without verification.

        Args:
            token: The JWT string

        Returns:
            The decoded header

        Note:
            This does not validate the token!
        """
        try:
            return jwt.get_unverified_header(token)
        except DecodeError as e:
            raise TokenValidationError(f"Failed to decode header: {e}") from e


def create_token(
    payload: dict[str, Any],
    secret: str | bytes,
    algorithm: str = "HS256",
) -> str:
    """Create a signed JWT.

    Args:
        payload: The claims to include
        secret: The signing secret/key
        algorithm: The signing algorithm

    Returns:
        The encoded JWT string
    """
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token_unsafe(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Decode a token without signature verification.

    WARNING: Only use this for debugging/inspection, never in production!

    Args:
        token: The JWT string

    Returns:
        Tuple of (header, payload)
    """
    header = jwt.get_unverified_header(token)
    payload = jwt.decode(token, options={"verify_signature": False})
    return header, payload

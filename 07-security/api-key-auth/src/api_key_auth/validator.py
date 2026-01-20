"""API key validation utilities.

This module provides validation functionality for API keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from api_key_auth.storage import APIKeyInfo, KeyStore, KeyStatus


class ValidationResult(Enum):
    """Result of key validation."""

    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RATE_LIMITED = "rate_limited"


@dataclass
class ValidationResponse:
    """Detailed response from key validation."""

    result: ValidationResult
    key_info: APIKeyInfo | None = None
    message: str | None = None
    details: dict[str, Any] | None = None


class APIKeyValidator:
    """Validates API keys against a store.

    Example:
        store = KeyStore()
        validator = APIKeyValidator(store)

        response = validator.validate(api_key)
        if response.result == ValidationResult.VALID:
            print(f"Valid key for {response.key_info.name}")
    """

    def __init__(
        self,
        store: KeyStore,
        required_prefix: str | None = None,
        allowed_tiers: list[str] | None = None,
    ):
        """Initialize the validator.

        Args:
            store: The key store to validate against
            required_prefix: Optional required key prefix
            allowed_tiers: Optional list of allowed key tiers
        """
        self.store = store
        self.required_prefix = required_prefix
        self.allowed_tiers = allowed_tiers

    def validate(self, key: str | None) -> ValidationResponse:
        """Validate an API key.

        Args:
            key: The API key to validate

        Returns:
            ValidationResponse with result and details
        """
        # Check if key is provided
        if not key:
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message="API key is required",
            )

        # Check prefix if required
        if self.required_prefix:
            if not key.startswith(f"{self.required_prefix}_"):
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    message=f"API key must start with '{self.required_prefix}_'",
                )

        # Look up key in store
        key_info = self.store.get_by_key(key)
        if not key_info:
            return ValidationResponse(
                result=ValidationResult.INVALID,
                message="Invalid API key",
            )

        # Check if revoked
        if key_info.is_revoked:
            return ValidationResponse(
                result=ValidationResult.REVOKED,
                key_info=key_info,
                message="API key has been revoked",
                details={"revoked_at": key_info.metadata.get("revoked_at")},
            )

        # Check if expired
        if key_info.is_expired:
            return ValidationResponse(
                result=ValidationResult.EXPIRED,
                key_info=key_info,
                message="API key has expired",
                details={"expired_at": key_info.expires_at.isoformat() if key_info.expires_at else None},
            )

        # Check tier if restricted
        if self.allowed_tiers:
            if key_info.tier.value not in self.allowed_tiers:
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    key_info=key_info,
                    message=f"API key tier '{key_info.tier.value}' not allowed",
                    details={"allowed_tiers": self.allowed_tiers},
                )

        # Key is valid
        return ValidationResponse(
            result=ValidationResult.VALID,
            key_info=key_info,
        )

    def is_valid(self, key: str | None) -> bool:
        """Quick check if a key is valid.

        Args:
            key: The API key to check

        Returns:
            True if valid
        """
        return self.validate(key).result == ValidationResult.VALID

    def require_valid(self, key: str | None) -> APIKeyInfo:
        """Validate a key and raise if invalid.

        Args:
            key: The API key to validate

        Returns:
            APIKeyInfo for valid keys

        Raises:
            ValueError: If key is invalid
        """
        response = self.validate(key)
        if response.result != ValidationResult.VALID:
            raise ValueError(response.message or "Invalid API key")
        assert response.key_info is not None
        return response.key_info


class ScopedValidator(APIKeyValidator):
    """Validator that checks for specific scopes/permissions."""

    def __init__(
        self,
        store: KeyStore,
        required_scopes: list[str] | None = None,
        **kwargs: Any,
    ):
        """Initialize the scoped validator.

        Args:
            store: The key store
            required_scopes: Scopes required for access
            **kwargs: Additional args for parent
        """
        super().__init__(store, **kwargs)
        self.required_scopes = required_scopes or []

    def validate(self, key: str | None) -> ValidationResponse:
        """Validate key including scope check.

        Args:
            key: The API key to validate

        Returns:
            ValidationResponse
        """
        # First do standard validation
        response = super().validate(key)
        if response.result != ValidationResult.VALID:
            return response

        # Check scopes
        if self.required_scopes and response.key_info:
            key_scopes = response.key_info.metadata.get("scopes", [])
            missing = [s for s in self.required_scopes if s not in key_scopes]

            if missing:
                return ValidationResponse(
                    result=ValidationResult.INVALID,
                    key_info=response.key_info,
                    message=f"Missing required scopes: {missing}",
                    details={
                        "required_scopes": self.required_scopes,
                        "key_scopes": key_scopes,
                        "missing_scopes": missing,
                    },
                )

        return response


def create_fastapi_dependency(validator: APIKeyValidator):
    """Create a FastAPI dependency for API key validation.

    Args:
        validator: The validator to use

    Returns:
        FastAPI dependency function

    Example:
        validator = APIKeyValidator(store)
        get_api_key = create_fastapi_dependency(validator)

        @app.get("/protected")
        async def protected(key_info: APIKeyInfo = Depends(get_api_key)):
            return {"owner": key_info.owner_id}
    """
    from typing import Annotated

    try:
        from fastapi import Depends, HTTPException, Security, status
        from fastapi.security import APIKeyHeader, APIKeyQuery

        api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
        api_key_query = APIKeyQuery(name="api_key", auto_error=False)

        async def get_api_key(
            header_key: str | None = Security(api_key_header),
            query_key: str | None = Security(api_key_query),
        ) -> APIKeyInfo:
            """FastAPI dependency that validates API key."""
            # Prefer header over query
            key = header_key or query_key

            response = validator.validate(key)

            if response.result == ValidationResult.INVALID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=response.message or "Invalid API key",
                    headers={"WWW-Authenticate": "ApiKey"},
                )

            if response.result == ValidationResult.REVOKED:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key has been revoked",
                )

            if response.result == ValidationResult.EXPIRED:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key has expired",
                )

            assert response.key_info is not None
            return response.key_info

        return get_api_key

    except ImportError:
        raise ImportError("FastAPI is required for this function. Install with: pip install fastapi")

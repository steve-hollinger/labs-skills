"""Claims validation utilities.

This module provides utilities for validating and extracting JWT claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class ClaimRule:
    """Rule for validating a claim.

    Attributes:
        name: The claim name
        required: Whether the claim is required
        validator: Optional validation function
        allowed_values: Optional list of allowed values
    """

    name: str
    required: bool = True
    validator: Callable[[Any], bool] | None = None
    allowed_values: list[Any] | None = None


class ClaimsValidator:
    """Validates JWT claims against configurable rules.

    Example:
        validator = ClaimsValidator()
        validator.add_rule(ClaimRule("sub", required=True))
        validator.add_rule(ClaimRule("role", allowed_values=["admin", "user"]))

        is_valid, errors = validator.validate(payload)
    """

    def __init__(self, rules: list[ClaimRule] | None = None):
        """Initialize the validator.

        Args:
            rules: Initial list of claim rules
        """
        self.rules: dict[str, ClaimRule] = {}
        if rules:
            for rule in rules:
                self.add_rule(rule)

    def add_rule(self, rule: ClaimRule) -> None:
        """Add a validation rule.

        Args:
            rule: The claim rule to add
        """
        self.rules[rule.name] = rule

    def remove_rule(self, name: str) -> None:
        """Remove a validation rule.

        Args:
            name: The claim name to remove
        """
        self.rules.pop(name, None)

    def validate(self, payload: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate claims against all rules.

        Args:
            payload: The decoded JWT payload

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        for name, rule in self.rules.items():
            # Check required claims
            if rule.required and name not in payload:
                errors.append(f"Missing required claim: {name}")
                continue

            if name not in payload:
                continue

            value = payload[name]

            # Check allowed values
            if rule.allowed_values is not None:
                if value not in rule.allowed_values:
                    errors.append(
                        f"Claim '{name}' has invalid value: {value}. "
                        f"Allowed: {rule.allowed_values}"
                    )

            # Run custom validator
            if rule.validator is not None:
                try:
                    if not rule.validator(value):
                        errors.append(f"Claim '{name}' failed custom validation")
                except Exception as e:
                    errors.append(f"Claim '{name}' validation error: {e}")

        return len(errors) == 0, errors


def validate_claims(
    payload: dict[str, Any],
    required: list[str] | None = None,
    issuer: str | None = None,
    audience: str | list[str] | None = None,
) -> tuple[bool, list[str]]:
    """Validate common JWT claims.

    Args:
        payload: The decoded JWT payload
        required: List of required claim names
        issuer: Expected issuer value
        audience: Expected audience value(s)

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors: list[str] = []
    now = datetime.now(timezone.utc).timestamp()

    # Check required claims
    if required:
        for claim in required:
            if claim not in payload:
                errors.append(f"Missing required claim: {claim}")

    # Check expiration
    if "exp" in payload:
        if payload["exp"] < now:
            errors.append("Token has expired")

    # Check not-before
    if "nbf" in payload:
        if payload["nbf"] > now:
            errors.append("Token is not yet valid (nbf)")

    # Check issuer
    if issuer and payload.get("iss") != issuer:
        errors.append(f"Invalid issuer: expected {issuer}, got {payload.get('iss')}")

    # Check audience
    if audience:
        token_aud = payload.get("aud")
        if isinstance(audience, str):
            audience = [audience]
        if isinstance(token_aud, str):
            token_aud = [token_aud]

        if token_aud is None or not any(a in token_aud for a in audience):
            errors.append(f"Invalid audience: expected {audience}, got {token_aud}")

    return len(errors) == 0, errors


def get_claim(
    payload: dict[str, Any],
    name: str,
    default: Any = None,
) -> Any:
    """Get a claim value from the payload.

    Args:
        payload: The decoded JWT payload
        name: The claim name
        default: Default value if claim not present

    Returns:
        The claim value or default
    """
    return payload.get(name, default)


def has_role(
    payload: dict[str, Any],
    role: str,
    roles_claim: str = "roles",
) -> bool:
    """Check if the token has a specific role.

    Args:
        payload: The decoded JWT payload
        role: The role to check for
        roles_claim: The claim name containing roles

    Returns:
        True if the role is present
    """
    roles = payload.get(roles_claim, [])
    if isinstance(roles, str):
        roles = [roles]
    return role in roles


def has_any_role(
    payload: dict[str, Any],
    roles: list[str],
    roles_claim: str = "roles",
) -> bool:
    """Check if the token has any of the specified roles.

    Args:
        payload: The decoded JWT payload
        roles: List of roles to check
        roles_claim: The claim name containing roles

    Returns:
        True if any role is present
    """
    return any(has_role(payload, role, roles_claim) for role in roles)


def has_all_roles(
    payload: dict[str, Any],
    roles: list[str],
    roles_claim: str = "roles",
) -> bool:
    """Check if the token has all of the specified roles.

    Args:
        payload: The decoded JWT payload
        roles: List of roles to check
        roles_claim: The claim name containing roles

    Returns:
        True if all roles are present
    """
    return all(has_role(payload, role, roles_claim) for role in roles)


def get_expiration(payload: dict[str, Any]) -> datetime | None:
    """Get the token expiration as a datetime.

    Args:
        payload: The decoded JWT payload

    Returns:
        The expiration datetime or None
    """
    exp = payload.get("exp")
    if exp is None:
        return None
    return datetime.fromtimestamp(exp, tz=timezone.utc)


def is_expired(payload: dict[str, Any], leeway: int = 0) -> bool:
    """Check if the token is expired.

    Args:
        payload: The decoded JWT payload
        leeway: Seconds of leeway to allow

    Returns:
        True if the token is expired
    """
    exp = get_expiration(payload)
    if exp is None:
        return False
    now = datetime.now(timezone.utc)
    return exp < now if leeway == 0 else exp.timestamp() + leeway < now.timestamp()

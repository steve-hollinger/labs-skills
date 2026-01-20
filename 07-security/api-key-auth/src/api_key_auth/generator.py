"""API key generation utilities.

This module provides functions for generating secure API keys.
"""

from __future__ import annotations

import re
import secrets
import string


def generate_api_key(
    prefix: str = "sk",
    length: int = 32,
    include_checksum: bool = False,
) -> str:
    """Generate a cryptographically secure API key.

    Args:
        prefix: Key prefix for identification (e.g., "sk_live", "pk_test")
        length: Length of the random portion in bytes (default 32 = ~43 chars)
        include_checksum: Whether to add a checksum suffix

    Returns:
        Generated API key string

    Example:
        >>> generate_api_key("sk_live")
        'sk_example_FAKE24CHARSTRING12sD7fG1hJkL2mN3oP4qR5s'
    """
    # Generate cryptographically secure random portion
    random_part = secrets.token_urlsafe(length)

    key = f"{prefix}_{random_part}"

    if include_checksum:
        # Simple checksum for format validation (not security)
        checksum = _calculate_checksum(key)
        key = f"{key}_{checksum:02d}"

    return key


def generate_key_pair(
    prefix_public: str = "pk",
    prefix_secret: str = "sk",
    environment: str = "live",
    length: int = 32,
) -> tuple[str, str]:
    """Generate a public/secret key pair.

    Args:
        prefix_public: Prefix for public key
        prefix_secret: Prefix for secret key
        environment: Environment suffix (e.g., "live", "test")
        length: Length of random portion

    Returns:
        Tuple of (public_key, secret_key)
    """
    public_prefix = f"{prefix_public}_{environment}"
    secret_prefix = f"{prefix_secret}_{environment}"

    return (
        generate_api_key(public_prefix, length),
        generate_api_key(secret_prefix, length),
    )


def _calculate_checksum(value: str) -> int:
    """Calculate a simple checksum for format validation.

    Args:
        value: The string to checksum

    Returns:
        Two-digit checksum (0-96)
    """
    return sum(ord(c) for c in value) % 97


def get_key_prefix(key: str, reveal_chars: int = 4) -> str:
    """Get a safe prefix representation of a key for display.

    Args:
        key: The full API key
        reveal_chars: Number of characters to reveal after prefix

    Returns:
        Safe display string (e.g., "sk_example_FAKE...")
    """
    parts = key.split("_")

    if len(parts) >= 2:
        # Show prefix and first few chars of random part
        prefix = "_".join(parts[:-1])  # Everything except last part
        random_part = parts[-1]
        return f"{prefix}_{random_part[:reveal_chars]}..."

    # Fallback for non-prefixed keys
    return f"{key[:8]}..."


def get_key_suffix(key: str, reveal_chars: int = 4) -> str:
    """Get the last few characters of a key for identification.

    Args:
        key: The full API key
        reveal_chars: Number of characters to reveal

    Returns:
        Suffix string (e.g., "...xyz9")
    """
    return f"...{key[-reveal_chars:]}"


def validate_key_format(
    key: str,
    expected_prefix: str | None = None,
    min_length: int = 20,
) -> tuple[bool, str | None]:
    """Validate the format of an API key.

    Args:
        key: The key to validate
        expected_prefix: Expected prefix (if any)
        min_length: Minimum total key length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not key:
        return False, "API key is required"

    if len(key) < min_length:
        return False, f"API key too short (minimum {min_length} characters)"

    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r"^[A-Za-z0-9_-]+$", key):
        return False, "API key contains invalid characters"

    # Check prefix if specified
    if expected_prefix:
        if not key.startswith(f"{expected_prefix}_"):
            return False, f"API key must start with '{expected_prefix}_'"

    return True, None


def parse_key_parts(key: str) -> dict[str, str]:
    """Parse an API key into its component parts.

    Args:
        key: The API key to parse

    Returns:
        Dictionary with key parts (prefix, environment, random, checksum)
    """
    parts = key.split("_")

    result: dict[str, str] = {}

    if len(parts) >= 2:
        result["type"] = parts[0]  # sk, pk, etc.

        # Check for environment
        if parts[1] in ("live", "test", "dev", "staging"):
            result["environment"] = parts[1]
            result["random"] = "_".join(parts[2:])
        else:
            result["random"] = "_".join(parts[1:])
    else:
        result["random"] = key

    return result


def mask_key(key: str, show_prefix: bool = True, show_suffix: int = 4) -> str:
    """Mask an API key for safe logging/display.

    Args:
        key: The API key to mask
        show_prefix: Whether to show the prefix portion
        show_suffix: Number of characters to show at the end

    Returns:
        Masked key string
    """
    parts = key.split("_")

    if len(parts) >= 2 and show_prefix:
        prefix = "_".join(parts[:-1])
        random_part = parts[-1]
        masked_random = "*" * (len(random_part) - show_suffix) + random_part[-show_suffix:]
        return f"{prefix}_{masked_random}"

    # Simple masking for non-prefixed keys
    if len(key) > show_suffix:
        return "*" * (len(key) - show_suffix) + key[-show_suffix:]

    return "*" * len(key)

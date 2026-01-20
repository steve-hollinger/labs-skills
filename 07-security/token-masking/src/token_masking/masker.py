"""Token masking utilities.

This module provides functions for masking sensitive data in various formats.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse, urlunparse

from token_masking.patterns import SECRET_PATTERNS, SecretDetector


def full_mask(value: str, placeholder: str = "***MASKED***") -> str:
    """Replace entire value with placeholder.

    Args:
        value: The value to mask
        placeholder: The replacement string

    Returns:
        The placeholder string
    """
    return placeholder


def partial_mask(
    value: str,
    show_start: int = 4,
    show_end: int = 4,
    placeholder: str = "***",
) -> str:
    """Mask value while showing first and last characters.

    Args:
        value: The value to mask
        show_start: Number of characters to show at start
        show_end: Number of characters to show at end
        placeholder: The masking placeholder

    Returns:
        Partially masked value
    """
    if len(value) <= show_start + show_end:
        return placeholder

    start = value[:show_start] if show_start > 0 else ""
    end = value[-show_end:] if show_end > 0 else ""
    return f"{start}{placeholder}{end}"


def mask_email(email: str) -> str:
    """Mask an email address while preserving format.

    Args:
        email: The email address to mask

    Returns:
        Masked email (e.g., "j***@example.com")
    """
    try:
        local, domain = email.split("@")
        if len(local) <= 1:
            masked_local = "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 1)
        return f"{masked_local}@{domain}"
    except ValueError:
        return "***@***"


def mask_url_credentials(url: str) -> str:
    """Mask credentials embedded in a URL.

    Args:
        url: The URL potentially containing credentials

    Returns:
        URL with password masked
    """
    try:
        parsed = urlparse(url)

        if not parsed.password:
            return url

        # Reconstruct netloc with masked password
        username = parsed.username or ""
        hostname = parsed.hostname or ""
        port_str = f":{parsed.port}" if parsed.port else ""

        netloc = f"{username}:***@{hostname}{port_str}"

        return urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        ))
    except Exception:
        # Fallback to regex-based masking
        return re.sub(r"(://[^:]+:)([^@]+)(@)", r"\1***\3", url)


def mask_json(
    data: Any,
    sensitive_fields: set[str] | None = None,
    mask_func: Any | None = None,
    case_insensitive: bool = True,
) -> Any:
    """Recursively mask sensitive fields in JSON-like data.

    Args:
        data: The data to mask (dict, list, or scalar)
        sensitive_fields: Set of field names to mask
        mask_func: Custom masking function (receives value, returns masked)
        case_insensitive: Whether to match field names case-insensitively

    Returns:
        Masked copy of the data
    """
    if sensitive_fields is None:
        sensitive_fields = {
            "password", "passwd", "pwd", "pass",
            "secret", "secret_key", "secretkey",
            "api_key", "apikey", "api_secret", "apisecret",
            "token", "access_token", "accesstoken",
            "refresh_token", "refreshtoken",
            "authorization", "auth", "auth_token",
            "private_key", "privatekey", "private",
            "ssn", "social_security",
            "credit_card", "creditcard", "card_number", "cardnumber",
            "cvv", "cvc", "pin",
            "aws_secret_access_key", "aws_secret",
        }

    if mask_func is None:
        mask_func = lambda x: "***MASKED***"

    # Normalize field names for comparison
    if case_insensitive:
        normalized_fields = {f.lower() for f in sensitive_fields}
        field_matches = lambda k: k.lower() in normalized_fields
    else:
        field_matches = lambda k: k in sensitive_fields

    if isinstance(data, dict):
        return {
            key: (
                mask_func(value) if field_matches(key)
                else mask_json(value, sensitive_fields, mask_func, case_insensitive)
            )
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [
            mask_json(item, sensitive_fields, mask_func, case_insensitive)
            for item in data
        ]

    return data


class TokenMasker:
    """High-level token masking utility.

    Provides comprehensive masking functionality for various data types.
    """

    def __init__(
        self,
        patterns: dict[str, str] | None = None,
        sensitive_fields: set[str] | None = None,
        show_start: int = 4,
        show_end: int = 4,
    ):
        """Initialize the masker.

        Args:
            patterns: Custom secret patterns for detection
            sensitive_fields: Custom sensitive field names for JSON masking
            show_start: Characters to show at start for partial masking
            show_end: Characters to show at end for partial masking
        """
        self.detector = SecretDetector(patterns or SECRET_PATTERNS)
        self.sensitive_fields = sensitive_fields
        self.show_start = show_start
        self.show_end = show_end

    def mask_secret(self, value: str) -> str:
        """Mask a secret value using partial masking.

        Args:
            value: The secret to mask

        Returns:
            Partially masked secret
        """
        return partial_mask(value, self.show_start, self.show_end)

    def mask_text(self, text: str) -> str:
        """Detect and mask all secrets in text.

        Args:
            text: The text to scan and mask

        Returns:
            Text with secrets masked
        """
        return self.detector.mask_all(text)

    def mask_data(self, data: Any) -> Any:
        """Mask sensitive data in structured data.

        Args:
            data: Dict, list, or scalar data

        Returns:
            Masked copy of the data
        """
        return mask_json(
            data,
            sensitive_fields=self.sensitive_fields,
            mask_func=self.mask_secret,
        )

    def mask_url(self, url: str) -> str:
        """Mask credentials in a URL.

        Args:
            url: The URL to mask

        Returns:
            URL with credentials masked
        """
        return mask_url_credentials(url)

    def mask_email(self, email: str) -> str:
        """Mask an email address.

        Args:
            email: The email to mask

        Returns:
            Masked email
        """
        return mask_email(email)

    def has_secrets(self, text: str) -> bool:
        """Check if text contains secrets.

        Args:
            text: The text to check

        Returns:
            True if secrets are detected
        """
        return self.detector.has_secrets(text)

    def detect_secrets(self, text: str) -> list[dict[str, Any]]:
        """Detect all secrets in text.

        Args:
            text: The text to scan

        Returns:
            List of detected secret info (type, position)
        """
        return [
            {
                "type": match.secret_type,
                "start": match.start,
                "end": match.end,
                "masked": match.masked,
            }
            for match in self.detector.detect(text)
        ]

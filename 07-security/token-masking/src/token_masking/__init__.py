"""Token Masking skill module.

This module provides utilities for masking sensitive data in logs,
outputs, and API responses.
"""

from token_masking.masker import (
    TokenMasker,
    full_mask,
    mask_email,
    mask_json,
    mask_url_credentials,
    partial_mask,
)
from token_masking.patterns import (
    SECRET_PATTERNS,
    SecretDetector,
    calculate_entropy,
    looks_like_secret,
)
from token_masking.logging_filter import (
    MaskingFilter,
    MaskingFormatter,
    setup_masked_logging,
)

__all__ = [
    # Masking functions
    "TokenMasker",
    "full_mask",
    "partial_mask",
    "mask_email",
    "mask_json",
    "mask_url_credentials",
    # Pattern detection
    "SECRET_PATTERNS",
    "SecretDetector",
    "calculate_entropy",
    "looks_like_secret",
    # Logging integration
    "MaskingFilter",
    "MaskingFormatter",
    "setup_masked_logging",
]

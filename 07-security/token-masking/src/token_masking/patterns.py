"""Secret detection patterns and utilities.

This module provides regex patterns for detecting common secret types
and entropy-based detection for unknown secret formats.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


# Common patterns for detecting secrets
SECRET_PATTERNS: dict[str, str] = {
    # AWS
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"(?i)aws_secret_access_key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})",

    # GitHub
    "github_pat": r"ghp_[A-Za-z0-9]{36}",
    "github_oauth": r"gho_[A-Za-z0-9]{36}",
    "github_app": r"ghs_[A-Za-z0-9]{36}",
    "github_refresh": r"ghr_[A-Za-z0-9]{36}",

    # Stripe
    "stripe_secret": r"sk_example_FAKE[A-Za-z0-9]{24,}",
    "stripe_publishable": r"pk_live_[A-Za-z0-9]{24,}",

    # Slack
    "slack_token": r"xox[baprs]-[0-9A-Za-z-]+",
    "slack_webhook": r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+",

    # Generic tokens
    "jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "bearer_token": r"(?i)bearer\s+[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",

    # Passwords in URLs
    "url_password": r"://[^:]+:([^@]+)@",

    # Generic secret patterns
    "generic_api_key": r"(?i)(api[_-]?key|apikey)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]{20,})",
    "generic_secret": r"(?i)(secret|password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?([^\s'\"]+)",
    "generic_token": r"(?i)(token|auth)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]{20,})",

    # Database connection strings
    "postgres_url": r"postgres(?:ql)?://[^:]+:([^@]+)@[^/]+/\w+",
    "mysql_url": r"mysql://[^:]+:([^@]+)@[^/]+/\w+",
    "mongodb_url": r"mongodb(?:\+srv)?://[^:]+:([^@]+)@[^/]+",

    # PII patterns
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone_us": r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",

    # Financial
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
}


def calculate_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string.

    Higher entropy suggests more randomness, which is characteristic of secrets.

    Args:
        data: The string to analyze

    Returns:
        Entropy value (0-8 for ASCII, higher is more random)
    """
    if not data:
        return 0.0

    counter = Counter(data)
    length = len(data)

    return -sum(
        (count / length) * math.log2(count / length)
        for count in counter.values()
    )


def looks_like_secret(
    value: str,
    min_entropy: float = 3.5,
    min_length: int = 8,
) -> bool:
    """Check if a value looks like a secret based on entropy.

    Args:
        value: The string to check
        min_entropy: Minimum entropy threshold (default 3.5)
        min_length: Minimum length for consideration (default 8)

    Returns:
        True if the value looks like a secret
    """
    if len(value) < min_length:
        return False

    # Check entropy
    return calculate_entropy(value) >= min_entropy


@dataclass
class SecretMatch:
    """A detected secret match."""

    secret_type: str
    value: str
    start: int
    end: int

    @property
    def masked(self) -> str:
        """Return masked version of the value."""
        if len(self.value) <= 8:
            return "***"
        return f"{self.value[:4]}***{self.value[-4:]}"


class SecretDetector:
    """Detect secrets using regex patterns and entropy analysis."""

    def __init__(
        self,
        patterns: dict[str, str] | None = None,
        use_entropy: bool = True,
        min_entropy: float = 4.0,
    ):
        """Initialize the detector.

        Args:
            patterns: Custom patterns to use (defaults to SECRET_PATTERNS)
            use_entropy: Whether to use entropy-based detection
            min_entropy: Minimum entropy for entropy-based detection
        """
        self.patterns = {
            name: re.compile(pattern)
            for name, pattern in (patterns or SECRET_PATTERNS).items()
        }
        self.use_entropy = use_entropy
        self.min_entropy = min_entropy

    def detect(self, text: str) -> list[SecretMatch]:
        """Find all secrets in text.

        Args:
            text: The text to scan

        Returns:
            List of SecretMatch objects
        """
        findings: list[SecretMatch] = []
        seen_positions: set[tuple[int, int]] = set()

        # Pattern-based detection
        for name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                # Get the actual secret value (may be in a group)
                if match.groups():
                    # Use the last group (usually the secret value)
                    value = match.group(len(match.groups()))
                    if value:
                        start = match.start(len(match.groups()))
                        end = match.end(len(match.groups()))
                    else:
                        value = match.group()
                        start = match.start()
                        end = match.end()
                else:
                    value = match.group()
                    start = match.start()
                    end = match.end()

                pos = (start, end)
                if pos not in seen_positions:
                    seen_positions.add(pos)
                    findings.append(SecretMatch(
                        secret_type=name,
                        value=value,
                        start=start,
                        end=end,
                    ))

        # Entropy-based detection for unknown patterns
        if self.use_entropy:
            # Find high-entropy strings not already detected
            words = re.findall(r"[A-Za-z0-9_-]{16,}", text)
            for word in words:
                if looks_like_secret(word, self.min_entropy):
                    # Check if already detected
                    start = text.find(word)
                    end = start + len(word)
                    pos = (start, end)

                    if pos not in seen_positions:
                        seen_positions.add(pos)
                        findings.append(SecretMatch(
                            secret_type="high_entropy",
                            value=word,
                            start=start,
                            end=end,
                        ))

        return sorted(findings, key=lambda m: m.start)

    def mask_all(self, text: str) -> str:
        """Detect and mask all secrets in text.

        Args:
            text: The text to mask

        Returns:
            Text with all detected secrets masked
        """
        findings = self.detect(text)

        # Mask from end to start to preserve positions
        result = text
        for match in reversed(findings):
            result = result[:match.start] + match.masked + result[match.end:]

        return result

    def has_secrets(self, text: str) -> bool:
        """Check if text contains any secrets.

        Args:
            text: The text to check

        Returns:
            True if secrets are detected
        """
        return len(self.detect(text)) > 0

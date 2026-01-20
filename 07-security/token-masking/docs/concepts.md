# Core Concepts

## Overview

Token masking is the practice of replacing sensitive data with placeholder values to prevent accidental exposure. This document covers the core concepts for effective data masking.

## Concept 1: What is Sensitive Data?

### What It Is

Sensitive data includes any information that could cause harm if exposed:
- **Authentication credentials**: Passwords, API keys, tokens
- **Personal Identifiable Information (PII)**: SSN, email, phone numbers
- **Financial data**: Credit card numbers, bank accounts
- **Infrastructure secrets**: Database passwords, private keys

### Why It Matters

Exposed sensitive data can lead to:
- **Security breaches**: Attackers gain access to systems
- **Compliance violations**: GDPR, PCI-DSS, HIPAA fines
- **Reputation damage**: Loss of customer trust
- **Financial loss**: Fraud, legal costs

### How to Identify

Sensitive data typically has recognizable patterns:

```python
# Common patterns for sensitive data
SENSITIVE_PATTERNS = {
    # API Keys
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"(?i)aws_secret_access_key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})",

    # Tokens
    "github_token": r"gh[ps]_[A-Za-z0-9]{36}",
    "jwt": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",

    # PII
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",

    # Financial
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
}
```

## Concept 2: Masking Strategies

### What It Is

Different masking strategies suit different use cases:

1. **Full Masking**: Replace entirely with placeholder
2. **Partial Masking**: Show prefix/suffix for identification
3. **Format-Preserving**: Maintain structure (e.g., email format)
4. **Tokenization**: Replace with reversible token

### Why It Matters

Choosing the right strategy balances security and usability:
- Full masking is most secure but provides no context
- Partial masking helps debugging while protecting core secret
- Format-preserving maintains data structure for testing

### How It Works

```python
def full_mask(value: str) -> str:
    """Replace entire value with placeholder."""
    return "***MASKED***"


def partial_mask(value: str, show_start: int = 4, show_end: int = 4) -> str:
    """Show first and last characters, mask middle."""
    if len(value) <= show_start + show_end:
        return full_mask(value)
    return f"{value[:show_start]}***{value[-show_end:]}"


def format_preserving_mask(email: str) -> str:
    """Mask email while preserving format."""
    local, domain = email.split("@")
    masked_local = local[0] + "*" * (len(local) - 1) if local else ""
    return f"{masked_local}@{domain}"


# Examples
full_mask("super-secret-password")      # "***MASKED***"
partial_mask("sk_example_FAKE")    # "sk_l***z789"
format_preserving_mask("user@example.com")  # "u***@example.com"
```

## Concept 3: Pattern Detection

### What It Is

Automatically detecting sensitive data in text using regex patterns and entropy analysis.

### Why It Matters

Manual identification of sensitive data is error-prone and doesn't scale. Automated detection catches secrets before they're logged or transmitted.

### How It Works

```python
import re
import math
from collections import Counter


def entropy(data: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in counter.values()
    )


def looks_like_secret(value: str, min_entropy: float = 3.5) -> bool:
    """Check if a value looks like a secret based on entropy."""
    if len(value) < 8:
        return False
    return entropy(value) >= min_entropy


class SecretDetector:
    """Detect secrets using patterns and entropy."""

    def __init__(self, patterns: dict[str, str]):
        self.patterns = {
            name: re.compile(pattern)
            for name, pattern in patterns.items()
        }

    def detect(self, text: str) -> list[tuple[str, str, int, int]]:
        """Find all secrets in text.

        Returns list of (type, value, start, end) tuples.
        """
        findings = []
        for name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                findings.append((name, match.group(), match.start(), match.end()))
        return findings

    def mask_all(self, text: str) -> str:
        """Detect and mask all secrets in text."""
        for name, pattern in self.patterns.items():
            text = pattern.sub(
                lambda m: partial_mask(m.group()),
                text
            )
        return text
```

## Concept 4: Logging Integration

### What It Is

Integrating masking with logging frameworks to automatically mask sensitive data before it's written to log files or sent to log aggregators.

### Why It Matters

- Logs are often stored long-term and widely accessible
- Log aggregation services may not be secured for sensitive data
- Developers may inadvertently log secrets during debugging

### How It Works

```python
import logging


class MaskingFilter(logging.Filter):
    """Filter that masks sensitive data in log records."""

    def __init__(self, detector: SecretDetector):
        super().__init__()
        self.detector = detector

    def filter(self, record: logging.LogRecord) -> bool:
        """Mask secrets in the log record."""
        # Mask the message
        if isinstance(record.msg, str):
            record.msg = self.detector.mask_all(record.msg)

        # Mask string arguments
        if record.args:
            record.args = tuple(
                self.detector.mask_all(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return True


# Usage
detector = SecretDetector(SENSITIVE_PATTERNS)
logger = logging.getLogger("myapp")
logger.addFilter(MaskingFilter(detector))

# Secrets are automatically masked
api_key = "sk_example_FAKE"
logger.info(f"Using API key: {api_key}")
# Output: Using API key: sk_l***z789
```

## Summary

Key takeaways:

1. **Identify sensitive data** using patterns and entropy analysis
2. **Choose appropriate masking** strategy for each data type
3. **Integrate with logging** to catch secrets automatically
4. **Test thoroughly** to avoid over-masking or under-masking
5. **Keep patterns updated** as new token formats emerge

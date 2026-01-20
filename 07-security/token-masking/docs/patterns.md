# Common Patterns

## Overview

This document covers common patterns and best practices for token masking implementations.

## Pattern 1: Configurable Masking Rules

### When to Use

When different environments or contexts require different masking behaviors.

### Implementation

```python
from dataclasses import dataclass, field
from enum import Enum


class MaskingStrategy(Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


@dataclass
class MaskingRule:
    """Configuration for masking a specific data type."""
    pattern: str
    strategy: MaskingStrategy = MaskingStrategy.PARTIAL
    show_start: int = 4
    show_end: int = 4
    placeholder: str = "***"


@dataclass
class MaskingConfig:
    """Global masking configuration."""
    rules: dict[str, MaskingRule] = field(default_factory=dict)
    default_strategy: MaskingStrategy = MaskingStrategy.PARTIAL

    @classmethod
    def from_dict(cls, data: dict) -> "MaskingConfig":
        """Create config from dictionary."""
        rules = {
            name: MaskingRule(**rule_data)
            for name, rule_data in data.get("rules", {}).items()
        }
        return cls(
            rules=rules,
            default_strategy=MaskingStrategy(data.get("default_strategy", "partial"))
        )


# Example configuration
config = MaskingConfig.from_dict({
    "default_strategy": "partial",
    "rules": {
        "password": {
            "pattern": r"(?i)password['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)",
            "strategy": "full",  # Always fully mask passwords
        },
        "api_key": {
            "pattern": r"sk_example_FAKE[A-Za-z0-9]+",
            "strategy": "partial",
            "show_start": 7,  # Show "sk_live"
            "show_end": 4,
        },
        "email": {
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "strategy": "partial",
            "show_start": 1,
            "show_end": 0,  # Show first char and domain
        },
    }
})
```

### Example

```python
class ConfigurableMasker:
    """Masker with configurable rules."""

    def __init__(self, config: MaskingConfig):
        self.config = config
        self._compiled = {
            name: re.compile(rule.pattern)
            for name, rule in config.rules.items()
        }

    def mask(self, text: str) -> str:
        """Apply all masking rules to text."""
        for name, pattern in self._compiled.items():
            rule = self.config.rules[name]
            text = pattern.sub(
                lambda m: self._apply_rule(m.group(), rule),
                text
            )
        return text

    def _apply_rule(self, value: str, rule: MaskingRule) -> str:
        """Apply a specific masking rule."""
        if rule.strategy == MaskingStrategy.NONE:
            return value
        if rule.strategy == MaskingStrategy.FULL:
            return rule.placeholder
        # Partial
        if len(value) <= rule.show_start + rule.show_end:
            return rule.placeholder
        return f"{value[:rule.show_start]}{rule.placeholder}{value[-rule.show_end:] if rule.show_end else ''}"
```

### Pitfalls to Avoid

- Don't make configuration too complex
- Always have sensible defaults
- Validate configuration at load time

## Pattern 2: JSON Field Masking

### When to Use

When dealing with structured data (JSON, dicts) where certain fields should always be masked.

### Implementation

```python
from typing import Any


def mask_json(
    data: Any,
    sensitive_fields: set[str] | None = None,
    mask_func: callable | None = None,
) -> Any:
    """Recursively mask sensitive fields in JSON-like data.

    Args:
        data: The data to mask (dict, list, or scalar)
        sensitive_fields: Set of field names to mask
        mask_func: Custom masking function, defaults to full mask

    Returns:
        Masked copy of the data
    """
    if sensitive_fields is None:
        sensitive_fields = {
            "password", "passwd", "pwd", "secret",
            "api_key", "apikey", "api_secret",
            "token", "access_token", "refresh_token",
            "authorization", "auth",
            "private_key", "privatekey",
            "ssn", "credit_card", "card_number",
        }

    if mask_func is None:
        mask_func = lambda x: "***MASKED***"

    if isinstance(data, dict):
        return {
            key: (
                mask_func(value) if key.lower() in sensitive_fields
                else mask_json(value, sensitive_fields, mask_func)
            )
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [mask_json(item, sensitive_fields, mask_func) for item in data]

    return data


# Example
data = {
    "user": "john",
    "password": "secret123",
    "settings": {
        "api_key": "sk_example_FAKE",
        "timeout": 30,
    },
    "tokens": ["token1", "token2"],  # List values not in sensitive fields
}

masked = mask_json(data)
# Result:
# {
#     "user": "john",
#     "password": "***MASKED***",
#     "settings": {
#         "api_key": "***MASKED***",
#         "timeout": 30,
#     },
#     "tokens": ["token1", "token2"],
# }
```

### Example

```python
# With custom masking function
def partial_mask(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"

masked = mask_json(data, mask_func=partial_mask)
```

### Pitfalls to Avoid

- Don't modify the original data (always copy)
- Handle nested structures recursively
- Consider case sensitivity in field names

## Pattern 3: URL Credential Masking

### When to Use

When dealing with connection strings that may contain embedded credentials.

### Implementation

```python
from urllib.parse import urlparse, urlunparse


def mask_url_credentials(url: str) -> str:
    """Mask credentials in a URL.

    Examples:
        postgres://user:password@host:5432/db -> postgres://user:***@host:5432/db
        https://api:secret@api.example.com -> https://api:***@api.example.com
    """
    try:
        parsed = urlparse(url)

        if parsed.password:
            # Reconstruct netloc with masked password
            if parsed.port:
                netloc = f"{parsed.username}:***@{parsed.hostname}:{parsed.port}"
            else:
                netloc = f"{parsed.username}:***@{parsed.hostname}"

            return urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            ))

        return url

    except Exception:
        # If parsing fails, try regex fallback
        return re.sub(
            r"(://[^:]+:)([^@]+)(@)",
            r"\1***\3",
            url
        )


# Examples
mask_url_credentials("postgres://admin:super-secret@db.example.com:5432/mydb")
# "postgres://admin:***@db.example.com:5432/mydb"

mask_url_credentials("redis://default:password123@cache.example.com")
# "redis://default:***@cache.example.com"
```

### Pitfalls to Avoid

- Handle URLs without credentials gracefully
- Preserve URL structure (ports, paths, query strings)
- Handle edge cases (special characters in passwords)

## Pattern 4: Exception Safe Logging

### When to Use

When exceptions might contain sensitive data in their messages.

### Implementation

```python
import functools
import traceback
from typing import Callable, TypeVar

T = TypeVar("T")


def safe_exception_logging(masker: "TokenMasker"):
    """Decorator that masks sensitive data in exception messages."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Mask the exception message
                safe_message = masker.mask_text(str(e))

                # Create a new exception with masked message
                new_exception = type(e)(safe_message)
                new_exception.__traceback__ = e.__traceback__
                raise new_exception from None

        return wrapper
    return decorator


# Usage
masker = TokenMasker()

@safe_exception_logging(masker)
def connect_to_database(connection_string: str):
    """Connect to database - exceptions will have credentials masked."""
    raise ConnectionError(f"Failed to connect to {connection_string}")

# Exception message will be masked:
# ConnectionError: Failed to connect to postgres://user:***@host/db
```

### Pitfalls to Avoid

- Don't swallow exceptions, only mask them
- Preserve exception type and traceback
- Consider performance impact of wrapping all functions

## Anti-Patterns

### Anti-Pattern 1: Regex-Only Detection

Relying only on regex misses secrets that don't match known patterns.

```python
# Bad - only catches known patterns
def detect_secrets(text: str) -> bool:
    return bool(re.search(r"AKIA[0-9A-Z]{16}", text))
```

### Better Approach

Combine regex with entropy analysis:

```python
def detect_secrets(text: str) -> bool:
    # Check known patterns
    if any(p.search(text) for p in KNOWN_PATTERNS):
        return True

    # Check for high-entropy strings
    for word in text.split():
        if len(word) > 12 and entropy(word) > 4.0:
            return True

    return False
```

### Anti-Pattern 2: Masking in Finally Block

Masking after data is already logged.

```python
# Bad - data logged before masking
try:
    result = api.call(secret_key)
except Exception as e:
    logger.error(f"API call failed: {e}")  # May contain secret
finally:
    secret_key = mask(secret_key)  # Too late!
```

### Better Approach

Mask before any operation that might log:

```python
# Good - mask early
safe_key = mask(secret_key)
try:
    result = api.call(secret_key)  # Use real key
except Exception as e:
    logger.error(f"API call with {safe_key} failed: {type(e).__name__}")
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Structured logging | JSON Field Masking |
| Connection strings | URL Credential Masking |
| Text/unstructured data | Pattern Detection with Regex |
| API responses | Configurable Masking Rules |
| Exception handling | Exception Safe Logging |
| Configuration files | Entropy + Pattern Detection |

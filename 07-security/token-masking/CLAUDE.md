# CLAUDE.md - Token Masking

This skill teaches how to mask sensitive data in logs, outputs, and API responses to prevent accidental exposure.

## Key Concepts

- **Token Detection**: Using regex patterns to identify sensitive data
- **Masking Strategies**: Full, partial, and pattern-based masking approaches
- **Logging Integration**: Filters and formatters for automatic masking
- **Configuration**: Customizable rules for different data types

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic token masking
make example-2  # Logging integration
make example-3  # Advanced pattern detection
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
token-masking/
├── src/token_masking/
│   ├── __init__.py
│   ├── masker.py          # Core masking utilities
│   ├── patterns.py        # Regex patterns for secrets
│   ├── logging_filter.py  # Logging integration
│   └── examples/
│       ├── example_1.py   # Basic masking
│       ├── example_2.py   # Logging integration
│       └── example_3.py   # Pattern detection
├── exercises/
│   ├── exercise_1.py      # Credit card masking
│   ├── exercise_2.py      # Custom formatter
│   ├── exercise_3.py      # Config scanner
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Secret Masking
```python
import re

def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value, showing only first/last characters."""
    if len(value) <= show_chars * 2:
        return "***MASKED***"
    return f"{value[:show_chars]}***{value[-show_chars:]}"
```

### Pattern 2: Regex-Based Detection
```python
SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "github_token": r"gh[ps]_[A-Za-z0-9]{36}",
    "stripe_key": r"sk_example_FAKE[A-Za-z0-9]{24}",
}

def detect_and_mask(text: str) -> str:
    """Detect and mask known secret patterns."""
    for name, pattern in SECRET_PATTERNS.items():
        text = re.sub(pattern, lambda m: mask_secret(m.group()), text)
    return text
```

### Pattern 3: Logging Filter
```python
import logging

class SecretMaskingFilter(logging.Filter):
    """Filter that masks secrets in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = detect_and_mask(record.msg)
        if record.args:
            record.args = tuple(
                detect_and_mask(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True
```

## Common Mistakes

1. **Not masking in exception messages**
   - Why: Exceptions often contain sensitive data
   - Fix: Create safe connection strings before use

2. **Over-aggressive masking**
   - Why: Makes debugging impossible
   - Fix: Show enough context (prefix/suffix)

3. **Missing patterns**
   - Why: New token types are always emerging
   - Fix: Keep pattern library updated, use entropy detection

4. **Masking after logging**
   - Why: Original data already written
   - Fix: Mask at the source, not the destination

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "What patterns should I detect?"
Start with common patterns in patterns.py:
- AWS credentials (AKIA..., aws_secret_access_key)
- API keys (sk_example_FAKE, pk_live_, ghp_, ghs_)
- Generic secrets (password, secret, token fields)
- JWTs (eyJ...)

### "How do I integrate with logging?"
Use the SecretMaskingFilter pattern:
```python
import logging
from token_masking import SecretMaskingFilter

logger = logging.getLogger()
logger.addFilter(SecretMaskingFilter())
```

### "What about JSON data?"
Use the mask_json function for recursive field masking:
```python
from token_masking import mask_json
safe_data = mask_json(data, sensitive_fields=["password", "api_key"])
```

## Testing Notes

- Tests verify masking works correctly
- Tests check for over-masking and under-masking
- Tests validate pattern detection accuracy
- Use parameterized tests for different token types

## Dependencies

Key dependencies in pyproject.toml:
- re (stdlib): Regex pattern matching
- logging (stdlib): Logging integration
- No external dependencies required

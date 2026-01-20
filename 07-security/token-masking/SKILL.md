---
name: masking-sensitive-tokens
description: This skill teaches how to mask sensitive data in logs, outputs, and API responses to prevent accidental exposure. Use when implementing authentication or verifying tokens.
---

# Token Masking

## Quick Start
```python
import re

def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value, showing only first/last characters."""
    if len(value) <= show_chars * 2:
        return "***MASKED***"
    return f"{value[:show_chars]}***{value[-show_chars:]}"
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic token masking
make example-2  # Logging integration
make example-3  # Advanced pattern detection
make test       # Run pytest
```

## Key Points
- Token Detection
- Masking Strategies
- Logging Integration

## Common Mistakes
1. **Not masking in exception messages** - Create safe connection strings before use
2. **Over-aggressive masking** - Show enough context (prefix/suffix)
3. **Missing patterns** - Keep pattern library updated, use entropy detection

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
---
name: implementing-api-key-auth
description: This skill teaches API key authentication patterns including key generation, storage, validation, and rate limiting for Python web applications. Use when implementing authentication or verifying tokens.
---

# Api Key Auth

## Quick Start
```python
import secrets

def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate a secure API key with prefix."""
    random_part = secrets.token_urlsafe(length)
    return f"{prefix}_{random_part}"
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic key generation
make example-2  # FastAPI middleware
make example-3  # Rate limiting
make test       # Run pytest
```

## Key Points
- Key Generation
- Key Storage
- Key Validation

## Common Mistakes
1. **Storing plain text keys** - Always hash keys before storing
2. **Keys in query parameters** - Use headers (X-API-Key)
3. **No rate limiting** - Implement per-key rate limits

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
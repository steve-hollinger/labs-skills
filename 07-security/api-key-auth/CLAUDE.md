# CLAUDE.md - API Key Authentication

This skill teaches API key authentication patterns including key generation, storage, validation, and rate limiting for Python web applications.

## Key Concepts

- **Key Generation**: Creating cryptographically secure, prefixed API keys
- **Key Storage**: Hashing keys before persistence (never store plain text)
- **Key Validation**: Middleware for validating keys on requests
- **Rate Limiting**: Preventing abuse with request limits per key

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Basic key generation
make example-2  # FastAPI middleware
make example-3  # Rate limiting
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
api-key-auth/
├── src/api_key_auth/
│   ├── __init__.py
│   ├── generator.py       # Key generation utilities
│   ├── storage.py         # Key storage and hashing
│   ├── validator.py       # Validation middleware
│   ├── rate_limiter.py    # Rate limiting
│   └── examples/
│       ├── example_1.py   # Basic generation
│       ├── example_2.py   # FastAPI integration
│       └── example_3.py   # Rate limiting
├── exercises/
│   ├── exercise_1.py      # SQLite storage
│   ├── exercise_2.py      # Key rotation
│   ├── exercise_3.py      # Tiered rate limits
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Key Generation
```python
import secrets

def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate a secure API key with prefix."""
    random_part = secrets.token_urlsafe(length)
    return f"{prefix}_{random_part}"
```

### Pattern 2: Key Hashing
```python
import hashlib

def hash_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()

def verify_key(key: str, key_hash: str) -> bool:
    """Verify a key against its hash."""
    return hash_key(key) == key_hash
```

### Pattern 3: FastAPI Dependency
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def validate_api_key(
    api_key: str = Security(api_key_header)
) -> APIKeyInfo:
    key_info = await key_store.get_by_key(api_key)
    if not key_info or key_info.revoked:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key_info
```

## Common Mistakes

1. **Storing plain text keys**
   - Why: Keys can be stolen if database is compromised
   - Fix: Always hash keys before storing

2. **Keys in query parameters**
   - Why: Logged in access logs, browser history
   - Fix: Use headers (X-API-Key)

3. **No rate limiting**
   - Why: Keys can be used for abuse
   - Fix: Implement per-key rate limits

4. **No key rotation**
   - Why: Long-lived keys increase risk
   - Fix: Support rotation with grace periods

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make examples` and the README.md.

### "How long should API keys be?"
Recommend at least 32 bytes of entropy (256 bits). Using secrets.token_urlsafe(32) gives approximately 256 bits.

### "Should I use API keys or JWTs?"
- API keys: Simple, long-lived, good for server-to-server
- JWTs: More complex, can carry claims, better for user auth
- Often used together: API key identifies the client, JWT identifies the user

### "How do I implement rate limiting?"
See example_3.py and rate_limiter.py. Use sliding window or token bucket algorithms. Consider using Redis for distributed systems.

## Testing Notes

- Tests use in-memory storage
- Tests verify hashing works correctly
- Tests check rate limiting behavior
- Mock time for testing expiration

## Dependencies

Key dependencies in pyproject.toml:
- fastapi: Web framework for examples
- cryptography: For secure key operations
- No required external storage (in-memory for demo)

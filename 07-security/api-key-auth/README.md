# API Key Authentication

Learn how to implement secure API key authentication in Python web applications. This skill covers key generation, storage, validation, rate limiting, and best practices for API key management.

## Learning Objectives

After completing this skill, you will be able to:
- Design secure API key authentication systems
- Generate cryptographically secure API keys
- Implement FastAPI middleware for key validation
- Store and manage API keys securely
- Add rate limiting to prevent abuse
- Rotate keys without downtime

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of HTTP and REST APIs

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### What is API Key Authentication?

API key authentication is a simple method for identifying and authenticating API clients. Each client receives a unique key that they include with every request.

```python
# Client sends key in header
curl -H "X-API-Key: sk_example_FAKE" https://api.example.com/data

# Or in query parameter (less secure)
curl "https://api.example.com/data?api_key=sk_example_FAKE"
```

### Key Components

1. **Key Generation**: Creating secure, unique identifiers
2. **Key Storage**: Hashing keys before storing (like passwords)
3. **Key Validation**: Verifying keys on each request
4. **Key Management**: Rotation, revocation, and expiration

### Key Format

A well-designed API key format includes:
- Prefix for identification (e.g., `sk_example_FAKE`, `pk_test_`)
- Random cryptographic portion
- Optional checksum for validation

```python
from api_key_auth import generate_api_key

# Generate a key with prefix
key = generate_api_key(prefix="sk_live")
# Returns: sk_example_FAKE24CHARSTRING12sD7f

# The prefix indicates:
# - sk = secret key (vs pk = public key)
# - live = production (vs test)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from api_key_auth import APIKeyValidator

app = FastAPI()
validator = APIKeyValidator(key_store)

@app.get("/protected")
async def protected_endpoint(
    api_key: str = Depends(validator.validate)
):
    return {"message": "Authenticated!"}
```

## Examples

### Example 1: Basic Key Generation and Validation

Generate keys and validate them against a store.

```bash
make example-1
```

### Example 2: FastAPI Middleware

Complete API key authentication for FastAPI applications.

```bash
make example-2
```

### Example 3: Rate Limiting and Key Rotation

Implement rate limits and key rotation strategies.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement a key store with SQLite persistence
2. **Exercise 2**: Build a key rotation system with grace periods
3. **Exercise 3**: Create a tiered rate limiting system based on key type

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Storing Keys in Plain Text
Always hash API keys before storage:
```python
# Bad - storing plain key
db.save(key=api_key)

# Good - hash before storing
key_hash = hashlib.sha256(api_key.encode()).hexdigest()
db.save(key_hash=key_hash)
```

### Keys in URL Query Parameters
Query strings appear in logs and browser history:
```python
# Bad - key in URL
GET /api/data?api_key=secret123

# Good - key in header
GET /api/data
X-API-Key: secret123
```

### No Rate Limiting
Without limits, keys can be abused:
```python
# Always implement rate limiting
rate_limiter = RateLimiter(requests_per_minute=60)

@app.get("/api/data")
async def get_data(key: APIKey = Depends(validate_key)):
    await rate_limiter.check(key.id)
    return data
```

### Not Invalidating Compromised Keys
Have a revocation mechanism ready:
```python
# Immediate revocation
key_store.revoke(key_id, reason="Compromised")

# Notification
await notify_key_owner(key_id, "Your API key has been revoked")
```

## Key Lifecycle

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Created │ -> │ Active  │ -> │ Rotated │ -> │ Revoked │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │
     │              │              │
     │         Rate Limited    Grace Period
     │              │              │
     v              v              v
  Stored         In Use        Expires
  (hashed)
```

## Security Considerations

| Consideration | Recommendation |
|---------------|----------------|
| Key Length | Minimum 32 bytes of entropy |
| Storage | Hash with SHA-256 or better |
| Transmission | Always use HTTPS |
| Rotation | Rotate every 90 days |
| Logging | Never log full key |
| Display | Show only last 4 characters |

## Further Reading

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- Related skills in this repository:
  - [JWT Validation](../jwt-validation/)
  - [OAuth 2.1/OIDC](../oauth-21-oidc/)
  - [Secrets Manager](../secrets-manager/)

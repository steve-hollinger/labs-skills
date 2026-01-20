# Token Masking

Learn how to securely mask sensitive data in logs, outputs, and API responses. This skill covers regex patterns for detecting tokens, implementation of masking utilities, and best practices for preventing accidental data exposure.

## Learning Objectives

After completing this skill, you will be able to:
- Identify sensitive data patterns (tokens, keys, passwords, PII)
- Implement robust masking functions using regex
- Create masking middleware for logging frameworks
- Handle edge cases and partial masking requirements
- Test masking implementations thoroughly

## Prerequisites

- Python 3.11+
- UV package manager
- Basic regex knowledge (helpful but not required)

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

### Why Mask Sensitive Data?

Sensitive data appearing in logs, error messages, or API responses can lead to:
- Security breaches if logs are compromised
- Compliance violations (PCI-DSS, GDPR, HIPAA)
- Accidental exposure to unauthorized personnel
- Data leaks through log aggregation services

```python
# Bad: Exposing secrets in logs
logger.info(f"Authenticating with API key: {api_key}")

# Good: Masking before logging
logger.info(f"Authenticating with API key: {mask_secret(api_key)}")
# Output: Authenticating with API key: sk_example_FAKE***...abc
```

### Masking Strategies

Different data types require different masking approaches:

```python
from token_masking import TokenMasker

masker = TokenMasker()

# Full masking (replace entirely)
masker.mask_password("super-secret")  # "***MASKED***"

# Partial masking (show prefix/suffix)
masker.mask_api_key("sk_example_FAKE")  # "sk_example_FAKE***...789"

# Pattern-based masking (email, phone)
masker.mask_email("user@example.com")  # "u***@example.com"

# JSON field masking
masker.mask_json({
    "username": "john",
    "password": "secret123",
    "api_key": "sk_example_FAKE"
})  # {"username": "john", "password": "***MASKED***", "api_key": "sk_***...xyz"}
```

### Common Token Patterns

| Token Type | Pattern | Example |
|------------|---------|---------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | AKIAIOSFODNN7EXAMPLE |
| AWS Secret Key | Base64, 40 chars | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY |
| GitHub Token | `gh[ps]_[A-Za-z0-9]{36}` | ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
| Stripe Key | `sk_example_FAKE[A-Za-z0-9]{24}` | sk_example_FAKE24CHARSTRING12 |
| JWT | `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+` | eyJhbGc... |
| Password in URL | `://[^:]+:([^@]+)@` | postgres://user:pass@host |

## Examples

### Example 1: Basic Token Masking

Implement simple masking functions for common secret types.

```bash
make example-1
```

### Example 2: Logging Integration

Create a masking filter for Python's logging framework.

```bash
make example-2
```

### Example 3: Advanced Pattern Detection

Build a comprehensive scanner that detects and masks multiple secret types.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement a credit card number masker with Luhn validation
2. **Exercise 2**: Create a custom logging formatter with configurable masking rules
3. **Exercise 3**: Build a sensitive data scanner for configuration files

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Over-Masking
Masking too aggressively can make debugging impossible:
```python
# Bad: Masks everything
def mask(s): return "***"

# Good: Preserve enough context for debugging
def mask(s): return f"{s[:4]}***{s[-4:]}" if len(s) > 8 else "***"
```

### Under-Masking
Not catching all sensitive patterns:
```python
# Bad: Only masks obvious patterns
masked = re.sub(r"password", "***", text)

# Good: Comprehensive pattern matching
patterns = [r"password", r"passwd", r"pwd", r"secret", r"api_key", ...]
```

### Masking After the Fact
Data may already be logged before masking:
```python
# Bad: Exception contains secret
try:
    connect(f"postgres://{user}:{password}@host")
except Exception as e:
    logger.error(e)  # Password in exception message!

# Good: Mask in connection string
safe_url = mask_url(f"postgres://{user}:{password}@host")
try:
    connect(safe_url)
except Exception as e:
    logger.error(e)  # Safe
```

## Further Reading

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Detect-Secrets by Yelp](https://github.com/Yelp/detect-secrets)
- Related skills in this repository:
  - [Secrets Manager](../secrets-manager/)
  - [JWT Validation](../jwt-validation/)

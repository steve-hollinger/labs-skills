# OAuth 2.1 and OpenID Connect

Learn modern OAuth 2.1 and OpenID Connect authentication patterns for Python applications.

## Quick Start

```bash
make setup      # Install dependencies
make examples   # Run example code
```

## What You'll Learn

1. **OAuth 2.1 Fundamentals** - Authorization Code + PKCE flow (the new standard)
2. **OpenID Connect** - Identity layer on top of OAuth
3. **Token Management** - Access tokens, refresh tokens, ID tokens
4. **Security Best Practices** - State validation, nonce handling, secure storage

## Prerequisites

- Python 3.11+
- UV package manager
- Understanding of HTTP and web authentication concepts

## Examples

| Example | Description |
|---------|-------------|
| `example_1.py` | Basic Authorization Code flow with PKCE |
| `example_2.py` | OIDC ID token validation |
| `example_3.py` | Token refresh and session management |

## Key Differences: OAuth 2.1 vs 2.0

| Feature | OAuth 2.0 | OAuth 2.1 |
|---------|-----------|-----------|
| PKCE | Optional | Required |
| Implicit Flow | Allowed | Removed |
| Resource Owner Password | Allowed | Removed |
| Refresh Token Rotation | Optional | Recommended |

## Documentation

- [docs/concepts.md](docs/concepts.md) - Core OAuth/OIDC concepts
- [docs/patterns.md](docs/patterns.md) - Implementation patterns

## Related Skills

- [jwt-validation](../jwt-validation/) - Validating JWT tokens
- [api-key-auth](../api-key-auth/) - Simple API authentication
- [secrets-manager](../secrets-manager/) - Secure credential storage

---
name: managing-aws-secrets
description: Secure secrets management using AWS Secrets Manager with Python boto3, including local development with LocalStack. Use when building or deploying containerized applications.
---

# Secrets Manager

## Quick Start
```python
def get_secrets_client(use_localstack: bool = False):
    """Get Secrets Manager client, optionally using LocalStack."""
    if use_localstack:
        return boto3.client(
            'secretsmanager',
            endpoint_url='http://localhost:4566',
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    return boto3.client('secretsmanager')
```


## Key Points
- Secret Storage
- Secret Rotation
- Versioning

## Common Mistakes
1. **Not using LocalStack for testing** - Always use LocalStack for local development and CI
2. **Logging secret values** - Never log secret values, only log secret names/operations
3. **Not handling secret rotation** - Implement TTL-based caching or rotation handlers

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
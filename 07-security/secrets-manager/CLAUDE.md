# CLAUDE.md - AWS Secrets Manager

This skill teaches secure secrets management using AWS Secrets Manager with Python boto3, including local development with LocalStack.

## Key Concepts

- **Secret Storage**: Encrypted key-value storage for sensitive data (credentials, API keys, certificates)
- **Secret Rotation**: Automatic periodic rotation of secrets without application changes
- **Versioning**: Track and access historical versions of secrets
- **LocalStack**: Local AWS emulator for development and testing without cloud costs

## Common Commands

```bash
make setup          # Install dependencies with UV
make localstack-up  # Start LocalStack container
make localstack-down # Stop LocalStack container
make examples       # Run all examples
make example-1      # Basic secret storage example
make example-2      # JSON secrets with versioning
make example-3      # Secret rotation patterns
make test           # Run pytest
make lint           # Run ruff and mypy
make clean          # Remove build artifacts
```

## Project Structure

```
secrets-manager/
├── src/secrets_manager/
│   ├── __init__.py
│   ├── client.py          # Secrets Manager client wrapper
│   └── examples/
│       ├── example_1.py   # Basic storage/retrieval
│       ├── example_2.py   # JSON secrets, versions
│       └── example_3.py   # Rotation patterns
├── exercises/
│   ├── exercise_1.py      # Config manager
│   ├── exercise_2.py      # Caching layer
│   ├── exercise_3.py      # Rotation handler
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: LocalStack Client Setup
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

### Pattern 2: Safe Secret Retrieval
```python
def get_secret(client, secret_name: str) -> dict | None:
    """Retrieve secret with proper error handling."""
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        return None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            return None
        raise
```

### Pattern 3: Secret Caching
```python
class CachedSecretManager:
    """Cache secrets to reduce API calls."""
    def __init__(self, client, ttl_seconds: int = 300):
        self.client = client
        self.ttl = ttl_seconds
        self._cache: dict[str, tuple[Any, float]] = {}

    def get_secret(self, name: str) -> Any:
        if name in self._cache:
            value, expiry = self._cache[name]
            if time.time() < expiry:
                return value
        # Fetch and cache
        secret = get_secret(self.client, name)
        self._cache[name] = (secret, time.time() + self.ttl)
        return secret
```

## Common Mistakes

1. **Not using LocalStack for testing**
   - Why: Testing against real AWS incurs costs and risks
   - Fix: Always use LocalStack for local development and CI

2. **Logging secret values**
   - Why: Secrets end up in log aggregators, violating security
   - Fix: Never log secret values, only log secret names/operations

3. **Not handling secret rotation**
   - Why: Cached secrets become stale after rotation
   - Fix: Implement TTL-based caching or rotation handlers

4. **Missing error handling**
   - Why: Secrets may not exist or may be inaccessible
   - Fix: Always catch ClientError and handle specific error codes

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make localstack-up && make examples` and the README.md.

### "How do I test without AWS credentials?"
Use LocalStack. Run `make localstack-up` and set `use_localstack=True` in client setup.

### "How do I rotate secrets?"
See example_3.py for rotation patterns. AWS uses a 4-step rotation protocol:
1. createSecret - Create new version
2. setSecret - Update the resource
3. testSecret - Verify new secret works
4. finishSecret - Mark as current

### "What's the best practice for caching?"
Use TTL-based caching (5 minutes default). See `CachedSecretManager` pattern above.

## Testing Notes

- Tests use pytest with LocalStack
- Requires Docker for LocalStack container
- Run `make localstack-up` before running tests
- Tests create/cleanup their own secrets

## Dependencies

Key dependencies in pyproject.toml:
- boto3: AWS SDK for Python
- moto: AWS service mocking for unit tests
- localstack-client: LocalStack integration helpers

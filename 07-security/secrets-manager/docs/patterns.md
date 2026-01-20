# Common Patterns

## Overview

This document covers common patterns and best practices for AWS Secrets Manager integration in Python applications.

## Pattern 1: Environment-Aware Client Factory

### When to Use

When building applications that need to run in multiple environments (local, staging, production) with different secret backends.

### Implementation

```python
import os
from enum import Enum
from functools import lru_cache

import boto3
from botocore.client import BaseClient


class Environment(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


@lru_cache(maxsize=1)
def get_secrets_client() -> BaseClient:
    """Get environment-appropriate Secrets Manager client.

    Uses LRU cache to reuse client instance (boto3 clients are thread-safe).
    """
    env = Environment(os.environ.get("ENVIRONMENT", "local"))

    if env == Environment.LOCAL:
        return boto3.client(
            'secretsmanager',
            endpoint_url=os.environ.get('LOCALSTACK_URL', 'http://localhost:4566'),
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )

    # Staging and Production use real AWS with IAM roles
    return boto3.client(
        'secretsmanager',
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
```

### Example

```python
# In your application code
client = get_secrets_client()
secret = client.get_secret_value(SecretId='myapp/database')
```

### Pitfalls to Avoid

- Don't create new clients for every request (performance impact)
- Don't hardcode environment detection logic
- Don't forget to handle the case where LocalStack isn't running

## Pattern 2: Cached Secret Manager

### When to Use

When you need to reduce API calls to Secrets Manager while maintaining reasonable freshness of secrets.

### Implementation

```python
import json
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any

import boto3
from botocore.exceptions import ClientError


@dataclass
class CachedSecret:
    """A cached secret with expiration time."""
    value: Any
    expires_at: float


class SecretCache:
    """Thread-safe secret cache with TTL expiration."""

    def __init__(
        self,
        client: Any = None,
        ttl_seconds: int = 300,
        refresh_before_expiry: int = 60
    ):
        self.client = client or boto3.client('secretsmanager')
        self.ttl = ttl_seconds
        self.refresh_buffer = refresh_before_expiry
        self._cache: dict[str, CachedSecret] = {}
        self._lock = Lock()

    def get_secret(self, secret_name: str, force_refresh: bool = False) -> Any:
        """Get a secret, using cache if valid."""
        now = time.time()

        with self._lock:
            if not force_refresh and secret_name in self._cache:
                cached = self._cache[secret_name]
                if now < cached.expires_at - self.refresh_buffer:
                    return cached.value

        # Fetch from Secrets Manager
        value = self._fetch_secret(secret_name)

        with self._lock:
            self._cache[secret_name] = CachedSecret(
                value=value,
                expires_at=now + self.ttl
            )

        return value

    def _fetch_secret(self, secret_name: str) -> Any:
        """Fetch secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response.get('SecretString')

            if secret_string:
                try:
                    return json.loads(secret_string)
                except json.JSONDecodeError:
                    return secret_string

            return response.get('SecretBinary')

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise KeyError(f"Secret not found: {secret_name}") from e
            raise

    def invalidate(self, secret_name: str | None = None) -> None:
        """Invalidate cache entries."""
        with self._lock:
            if secret_name:
                self._cache.pop(secret_name, None)
            else:
                self._cache.clear()
```

### Example

```python
# Create a global cache instance
secret_cache = SecretCache(ttl_seconds=300)

# Use throughout application
db_config = secret_cache.get_secret('myapp/database')
api_key = secret_cache.get_secret('myapp/external-api')

# Force refresh after rotation
secret_cache.get_secret('myapp/database', force_refresh=True)

# Invalidate on rotation notification
secret_cache.invalidate('myapp/database')
```

### Pitfalls to Avoid

- Don't set TTL too long (stale secrets after rotation)
- Don't set TTL too short (excessive API calls)
- Don't forget thread safety in multi-threaded applications

## Pattern 3: Configuration Loader

### When to Use

When you want to load application configuration from Secrets Manager with validation and type safety.

### Implementation

```python
from dataclasses import dataclass
from typing import TypeVar, Type
import json

from pydantic import BaseModel, ValidationError


class DatabaseConfig(BaseModel):
    """Database configuration schema."""
    host: str
    port: int = 5432
    username: str
    password: str
    database: str
    ssl_mode: str = "require"


class APIConfig(BaseModel):
    """External API configuration."""
    api_key: str
    base_url: str
    timeout_seconds: int = 30


T = TypeVar('T', bound=BaseModel)


class ConfigLoader:
    """Load and validate configuration from Secrets Manager."""

    def __init__(self, client, prefix: str = ""):
        self.client = client
        self.prefix = prefix

    def load(self, secret_name: str, schema: Type[T]) -> T:
        """Load and validate a secret against a Pydantic schema."""
        full_name = f"{self.prefix}/{secret_name}" if self.prefix else secret_name

        response = self.client.get_secret_value(SecretId=full_name)
        secret_data = json.loads(response['SecretString'])

        try:
            return schema.model_validate(secret_data)
        except ValidationError as e:
            raise ValueError(
                f"Secret {full_name} does not match schema {schema.__name__}: {e}"
            ) from e
```

### Example

```python
# Load typed configuration
loader = ConfigLoader(client, prefix="myapp")

db_config = loader.load("database", DatabaseConfig)
print(f"Connecting to {db_config.host}:{db_config.port}")

api_config = loader.load("external-api", APIConfig)
print(f"API endpoint: {api_config.base_url}")
```

### Pitfalls to Avoid

- Don't skip validation (secrets can have unexpected formats)
- Don't expose validation errors in logs (may contain partial secrets)
- Don't forget to handle schema evolution

## Pattern 4: Secret Rotation Handler

### When to Use

When implementing custom secret rotation for resources not covered by AWS-provided rotation functions.

### Implementation

```python
import json
import secrets
import string
from abc import ABC, abstractmethod
from typing import Any

import boto3


class RotationHandler(ABC):
    """Base class for secret rotation handlers."""

    def __init__(self, client=None):
        self.client = client or boto3.client('secretsmanager')

    def handle_rotation(self, event: dict[str, Any]) -> None:
        """Main rotation handler entry point."""
        secret_id = event['SecretId']
        token = event['ClientRequestToken']
        step = event['Step']

        handlers = {
            'createSecret': self.create_secret,
            'setSecret': self.set_secret,
            'testSecret': self.test_secret,
            'finishSecret': self.finish_secret,
        }

        handler = handlers.get(step)
        if not handler:
            raise ValueError(f"Unknown rotation step: {step}")

        handler(secret_id, token)

    def create_secret(self, secret_id: str, token: str) -> None:
        """Create new secret version with AWSPENDING stage."""
        # Check if pending version already exists
        try:
            self.client.get_secret_value(
                SecretId=secret_id,
                VersionId=token,
                VersionStage='AWSPENDING'
            )
            return  # Already created
        except self.client.exceptions.ResourceNotFoundException:
            pass

        # Get current secret
        current = self.client.get_secret_value(
            SecretId=secret_id,
            VersionStage='AWSCURRENT'
        )
        current_secret = json.loads(current['SecretString'])

        # Generate new secret
        new_secret = self.generate_new_secret(current_secret)

        # Store as pending
        self.client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps(new_secret),
            VersionStages=['AWSPENDING']
        )

    @abstractmethod
    def generate_new_secret(self, current: dict[str, Any]) -> dict[str, Any]:
        """Generate new secret values. Override in subclass."""
        pass

    @abstractmethod
    def set_secret(self, secret_id: str, token: str) -> None:
        """Apply new secret to the resource. Override in subclass."""
        pass

    @abstractmethod
    def test_secret(self, secret_id: str, token: str) -> None:
        """Test that new secret works. Override in subclass."""
        pass

    def finish_secret(self, secret_id: str, token: str) -> None:
        """Move AWSCURRENT to new version."""
        metadata = self.client.describe_secret(SecretId=secret_id)

        # Find current version
        current_version = None
        for version_id, stages in metadata['VersionIdsToStages'].items():
            if 'AWSCURRENT' in stages:
                if version_id == token:
                    return  # Already current
                current_version = version_id
                break

        # Move AWSCURRENT to pending version
        self.client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId=current_version
        )


def generate_password(length: int = 32) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

### Example

```python
class DatabaseRotationHandler(RotationHandler):
    """Rotate database password."""

    def generate_new_secret(self, current: dict[str, Any]) -> dict[str, Any]:
        return {
            **current,
            'password': generate_password(32)
        }

    def set_secret(self, secret_id: str, token: str) -> None:
        pending = self.client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage='AWSPENDING'
        )
        secret = json.loads(pending['SecretString'])

        # Update database user password
        # (Implementation depends on your database)
        update_db_password(
            secret['username'],
            secret['password']
        )

    def test_secret(self, secret_id: str, token: str) -> None:
        pending = self.client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage='AWSPENDING'
        )
        secret = json.loads(pending['SecretString'])

        # Verify connection works
        test_db_connection(secret)
```

### Pitfalls to Avoid

- Don't forget to handle idempotency (rotation can be retried)
- Don't update the resource before storing AWSPENDING
- Don't skip the test step

## Anti-Patterns

### Anti-Pattern 1: Environment Variables for Secrets

Storing secrets in environment variables exposes them in process listings and crash dumps.

```python
# Bad - secrets in environment
import os
database_password = os.environ['DATABASE_PASSWORD']
```

### Better Approach

```python
# Good - fetch from Secrets Manager
from secret_cache import secret_cache

db_config = secret_cache.get_secret('myapp/database')
database_password = db_config['password']
```

### Anti-Pattern 2: Hardcoded Secret Names

Hardcoding secret names makes environment promotion difficult.

```python
# Bad - hardcoded
secret = client.get_secret_value(SecretId='prod/myapp/database')
```

### Better Approach

```python
# Good - configurable
import os
secret_name = os.environ['DATABASE_SECRET_NAME']  # Set per environment
secret = client.get_secret_value(SecretId=secret_name)
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Single secret access | Direct client call |
| Frequent secret access | Cached Secret Manager |
| Multiple environments | Environment-Aware Factory |
| Typed configuration | Configuration Loader |
| Custom resource rotation | Rotation Handler |
| Lambda functions | Direct + Environment Variables for names |

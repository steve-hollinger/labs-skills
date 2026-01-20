# Common Patterns

## Overview

This document covers common patterns and best practices for Dynaconf configuration management.

## Pattern 1: Application Settings Module

### When to Use

When building any Python application that needs configuration. Create a dedicated settings module that's imported throughout the application.

### Implementation

```python
# config.py
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    envvar_prefix="MYAPP",
    environments=True,
    env_switcher="MYAPP_ENV",
    load_dotenv=True,  # Load .env file if present
)
```

```toml
# settings.toml
[default]
app_name = "MyApplication"
debug = false
log_level = "INFO"

[default.server]
host = "0.0.0.0"
port = 8000

[default.database]
driver = "postgresql"
host = "localhost"
port = 5432
name = "myapp"

[development]
debug = true
log_level = "DEBUG"
database.name = "myapp_dev"

[production]
log_level = "WARNING"
server.workers = 4
```

### Example

```python
# app.py
from config import settings

def create_app():
    app = Application(
        name=settings.app_name,
        debug=settings.debug,
    )
    app.configure_database(
        host=settings.database.host,
        port=settings.database.port,
        name=settings.database.name,
    )
    return app
```

### Pitfalls to Avoid

- Don't import settings inside functions (do it at module level)
- Don't create multiple Dynaconf instances (singleton pattern)
- Don't hardcode the config file path (use relative paths)

## Pattern 2: FastAPI/Flask Integration

### When to Use

When building web applications with FastAPI or Flask that need configuration.

### Implementation

```python
# config.py
from functools import lru_cache
from dynaconf import Dynaconf

@lru_cache
def get_settings() -> Dynaconf:
    """Get cached settings instance."""
    return Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],
        envvar_prefix="APP",
        environments=True,
    )

settings = get_settings()
```

```python
# main.py (FastAPI)
from fastapi import FastAPI, Depends
from config import settings, get_settings
from dynaconf import Dynaconf

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Use as dependency for testing
def get_config() -> Dynaconf:
    return get_settings()

@app.get("/info")
def info(config: Dynaconf = Depends(get_config)):
    return {"app": config.app_name, "version": config.version}
```

### Example

```python
# For testing, you can override the dependency
from fastapi.testclient import TestClient

def get_test_settings():
    return Dynaconf(
        settings_files=["test_settings.toml"],
        environments=False,
    )

app.dependency_overrides[get_config] = get_test_settings
client = TestClient(app)
```

### Pitfalls to Avoid

- Don't read settings in every request (cache them)
- Don't use settings before app startup is complete
- Remember to handle missing settings gracefully

## Pattern 3: Multi-Service Configuration

### When to Use

When you have multiple services/components that share some configuration but have unique settings.

### Implementation

```toml
# settings.toml

# Shared settings for all services
[default]
log_level = "INFO"
metrics_enabled = true

[default.kafka]
bootstrap_servers = ["localhost:9092"]
group_id_prefix = "myapp"

# API Service specific
[default.api]
host = "0.0.0.0"
port = 8000
cors_origins = ["http://localhost:3000"]

# Worker Service specific
[default.worker]
concurrency = 4
task_timeout = 300
queue = "default"

# Database shared but configurable
[default.database]
host = "localhost"
port = 5432
pool_size = 5

# Production overrides
[production]
log_level = "WARNING"
database.host = "prod-db.internal"
database.pool_size = 20
api.cors_origins = ["https://myapp.com"]
worker.concurrency = 16
```

```python
# api/config.py
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    envvar_prefix="API",
    environments=True,
)

# Access API-specific settings
port = settings.api.port
cors = settings.api.cors_origins

# Access shared settings
log_level = settings.log_level
db_host = settings.database.host
```

```python
# worker/config.py
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml"],
    envvar_prefix="WORKER",
    environments=True,
)

# Access worker-specific settings
concurrency = settings.worker.concurrency

# Override via env: WORKER_WORKER__CONCURRENCY=8
```

### Pitfalls to Avoid

- Don't duplicate shared settings in each service
- Use consistent naming conventions across services
- Consider using a base config module that others extend

## Pattern 4: Secrets with Vault/Cloud

### When to Use

When deploying to production environments where secrets should come from external secret managers.

### Implementation

```python
# config.py
import os
from dynaconf import Dynaconf

def load_secrets_from_vault(settings: Dynaconf) -> None:
    """Load secrets from HashiCorp Vault in production."""
    if settings.current_env != "production":
        return

    import hvac
    client = hvac.Client(url=os.environ["VAULT_ADDR"])
    client.token = os.environ["VAULT_TOKEN"]

    secrets = client.secrets.kv.v2.read_secret_version(
        path="myapp/config"
    )["data"]["data"]

    for key, value in secrets.items():
        settings.set(key, value)

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    envvar_prefix="MYAPP",
    environments=True,
)

# Post-load hook for vault secrets
load_secrets_from_vault(settings)
```

### AWS Secrets Manager Pattern

```python
import json
import boto3
from dynaconf import Dynaconf

def load_aws_secrets(settings: Dynaconf) -> None:
    """Load secrets from AWS Secrets Manager."""
    if settings.get("USE_AWS_SECRETS", False):
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(
            SecretId=settings.AWS_SECRET_NAME
        )
        secrets = json.loads(response["SecretString"])
        for key, value in secrets.items():
            settings.set(key.upper(), value)

settings = Dynaconf(...)
load_aws_secrets(settings)
```

### Pitfalls to Avoid

- Don't commit any secrets, even for development
- Always have fallbacks for local development
- Log which secret source is being used (not the values!)

## Pattern 5: Configuration Validation

### When to Use

Always. Every application should validate its configuration at startup.

### Implementation

```python
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    settings_files=["settings.toml"],
    validators=[
        # Required in all environments
        Validator("APP_NAME", must_exist=True),
        Validator("DATABASE_URL", must_exist=True),

        # Type validation
        Validator("PORT", is_type_of=int, gte=1024, lte=65535),
        Validator("DEBUG", is_type_of=bool, default=False),
        Validator("WORKERS", is_type_of=int, gte=1, default=4),

        # Production-specific
        Validator("DEBUG", eq=False, env="production"),
        Validator("SSL_ENABLED", eq=True, env="production"),

        # Conditional validation
        Validator(
            "SSL_CERT_PATH",
            must_exist=True,
            when=Validator("SSL_ENABLED", eq=True)
        ),
        Validator(
            "SSL_KEY_PATH",
            must_exist=True,
            when=Validator("SSL_ENABLED", eq=True)
        ),

        # Custom validation with condition
        Validator(
            "WORKERS",
            gte=2,
            env="production",
            messages={"condition": "Production requires at least 2 workers"}
        ),
    ],
)

# Validation happens automatically on instantiation
# To validate manually (e.g., after setting values):
# settings.validators.validate()
```

### Pitfalls to Avoid

- Don't skip validation in development
- Provide helpful error messages
- Validate early (at import time, not first use)

## Anti-Patterns

### Anti-Pattern 1: Scattered Configuration

Don't access environment variables directly throughout the code:

```python
# Bad - scattered env var access
def connect_db():
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    ...

def send_email():
    smtp_host = os.environ.get("SMTP_HOST")
    ...
```

### Better Approach

```python
# Good - centralized configuration
# config.py
from dynaconf import Dynaconf
settings = Dynaconf(...)

# db.py
from config import settings

def connect_db():
    host = settings.database.host
    port = settings.database.port
    ...
```

### Anti-Pattern 2: Environment Checks in Code

Don't check environment names in business logic:

```python
# Bad - environment checks everywhere
def get_api_url():
    if os.environ.get("ENV") == "production":
        return "https://api.example.com"
    else:
        return "http://localhost:8000"
```

### Better Approach

```toml
# settings.toml
[development]
api_url = "http://localhost:8000"

[production]
api_url = "https://api.example.com"
```

```python
# Good - just use the setting
def get_api_url():
    return settings.api_url
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Single application | Application Settings Module |
| Web application | FastAPI/Flask Integration |
| Microservices | Multi-Service Configuration |
| Cloud deployment | Secrets with Vault/Cloud |
| Any application | Configuration Validation |

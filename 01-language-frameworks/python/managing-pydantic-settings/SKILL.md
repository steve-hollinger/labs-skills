---
name: managing-pydantic-settings
description: Manage environment-specific configuration with Pydantic v2 Settings. Use when handling app configuration, secrets, and environment variables.
tags: ['python', 'pydantic', 'configuration', 'settings', 'env-vars']
---

# Pydantic Configuration Management

## Quick Start
```python
# src/config.py
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration using Pydantic v2."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service metadata
    service_name: str = Field(default="my-service")
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")

    # AWS configuration
    aws_region: str = Field(default="us-east-1")

    # Kafka configuration
    kafka_brokers: str = Field(default="localhost:9092")
    kafka_topic: str
    kafka_consumer_group: str

    @field_validator("kafka_brokers")
    @classmethod
    def validate_kafka_brokers(cls, v: str) -> str:
        """Ensure Kafka brokers are properly formatted."""
        if not v:
            raise ValueError("kafka_brokers cannot be empty")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Usage
settings = get_settings()
print(f"Running in {settings.environment}")
```

## Key Points
- **Environment-specific configuration**: Use Literal types to enforce valid environments (dev, stage, preprod, prod) and provide appropriate defaults for each
- **Validation at startup**: Pydantic validates all settings when the application starts, catching configuration errors early before runtime
- **Type safety**: Field annotations provide IDE autocomplete and type checking, reducing configuration-related bugs
- **Flexible sourcing**: Settings can be loaded from environment variables, .env files, or AWS Secrets Manager with consistent validation
- **Caching with @lru_cache**: Settings instances are cached to avoid repeated environment variable reads and validation overhead

## Common Mistakes
1. **Forgetting @lru_cache on get_settings()** - Without caching, Settings is re-instantiated and re-validated on every call, causing performance issues. Always decorate factory functions with @lru_cache.
2. **Using Pydantic v1 Config class instead of model_config** - Pydantic v2 changed configuration syntax. Use `model_config = SettingsConfigDict(...)` not `class Config:`.
3. **Not providing defaults for optional settings** - Missing defaults cause ValidationError when env vars aren't set. Always provide sensible defaults for non-critical settings.
4. **Storing secrets in .env files in git** - Never commit .env files with secrets. Add .env to .gitignore and use AWS Secrets Manager for sensitive values in production.
5. **Mixing case sensitivity** - Environment variables are case-sensitive by default. Set `case_sensitive=False` in SettingsConfigDict to avoid mismatches between ENV_VAR and env_var.

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples

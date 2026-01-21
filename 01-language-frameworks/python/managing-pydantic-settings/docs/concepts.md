# Core Concepts: Pydantic Configuration Management

## What

Pydantic v2 Settings is a framework for managing environment-specific application configuration with automatic validation and type safety. It extends Pydantic's data validation to load configuration from environment variables, .env files, and external secret stores, validating all settings at application startup.

The core component is `BaseSettings`, a Pydantic model that automatically reads from environment variables matching field names. Combined with `Field` definitions and validators, it provides a type-safe, validated configuration layer that adapts to different environments (dev, stage, preprod, prod) without code changes.

## Why

### The Problem

Without a configuration management framework, applications face several challenges:

- **Scattered configuration**: Settings spread across multiple files, environment variables, and hardcoded values make it hard to understand what configuration exists
- **Runtime errors**: Type mismatches and missing values aren't discovered until that code path executes in production
- **Environment inconsistency**: Different environments (dev, stage, prod) require different configurations, leading to brittle if/else logic
- **Security risks**: Secrets mixed with regular config, making it easy to accidentally log or expose sensitive values
- **Poor developer experience**: No autocomplete, type checking, or validation means constant reference to documentation

### The Solution

Pydantic Settings provides a centralized, validated configuration approach:

- **Single source of truth**: All configuration defined in one Settings class with clear types and defaults
- **Fail-fast validation**: Invalid configuration causes immediate startup failure with clear error messages, not silent runtime bugs
- **Environment awareness**: Same code adapts to dev/stage/prod using environment variables and .env files
- **Type safety**: IDE autocomplete and mypy catch configuration mistakes before runtime
- **Secrets integration**: Clean separation between regular config and sensitive values loaded from AWS Secrets Manager

### Fetch Context

At Fetch, services run across multiple environments with different infrastructure:

- **Dev**: Local development with Docker Compose, localhost services, relaxed validation
- **Stage**: AWS-based testing environment with real infrastructure but synthetic data
- **Preprod**: Production-like environment for final validation before release
- **Prod**: Production with strict validation, monitoring, and real customer data

Pydantic Settings enables a single codebase to adapt to these environments using FSD-provided environment variables (KAFKA_BROKERS, AWS_REGION, etc.) while maintaining type safety and validation.



## How

### Settings Class Architecture

A Pydantic Settings class combines several components:

**1. BaseSettings inheritance**: Extends Pydantic BaseSettings to enable environment variable loading
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
```

**2. Field definitions**: Type-annotated fields with validation rules and defaults
```python
from pydantic import Field

kafka_brokers: str = Field(default="localhost:9092")
kafka_topic: str  # Required, no default
port: int = Field(default=8000, ge=1, le=65535)
```

**3. Field validators**: Custom validation logic for complex requirements
```python
from pydantic import field_validator

@field_validator("kafka_brokers")
@classmethod
def validate_kafka_brokers(cls, v: str) -> str:
    if not v:
        raise ValueError("kafka_brokers cannot be empty")
    return v
```

**4. Environment file loading**: Automatic loading from .env files for local development
```python
# .env file
KAFKA_TOPIC=user-events
KAFKA_CONSUMER_GROUP=my-service-consumer
```

**5. Secrets integration**: Loading sensitive values from AWS Secrets Manager
```python
import boto3
import json

def load_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
```

### Design Patterns

**Singleton pattern with @lru_cache**: Settings should be instantiated once and reused
```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Environment-specific defaults**: Use Literal types for constrained values
```python
from typing import Literal

environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")
```

**Computed properties**: Derive values from base settings
```python
@property
def kafka_broker_list(self) -> list[str]:
    return [b.strip() for b in self.kafka_brokers.split(",")]
```

## When to Use

**Use when:**
- Building services that run in multiple environments (dev/stage/prod) with different configurations
- Managing 10+ configuration values that need validation and type safety
- Integrating with external services (Kafka, databases, APIs) that require connection details
- Loading secrets from AWS Secrets Manager or other external sources
- Creating microservices where configuration consistency is critical

**Avoid when:**
- Building CLI tools that need simple argument parsing (use argparse or click instead)
- Managing constant values that never change across environments (use Python constants)
- Working with complex hierarchical config files (consider YAML/JSON loaders)
- Building single-script utilities with 2-3 simple settings (environment variables are sufficient)

## Key Terminology

- **BaseSettings** - The Pydantic class that enables automatic loading from environment variables and validation of configuration settings
- **Field** - Pydantic's descriptor for defining validation rules, defaults, and metadata for individual settings fields
- **field_validator** - Decorator for custom validation functions that run after type conversion but before the model is instantiated
- **env_prefix** - Configuration option to add a prefix to all environment variable names (e.g., `env_prefix="APP_"` makes `service_name` read from `APP_SERVICE_NAME`)
- **SettingsConfigDict** - Pydantic v2's configuration object for customizing Settings behavior (replaces v1's `Config` class)
- **@lru_cache** - Python decorator that caches function results, used with `get_settings()` to ensure singleton pattern for Settings instances

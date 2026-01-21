# Code Patterns: Pydantic Configuration Management

## Pattern 1: Basic Settings with Environment Variables

**When to Use:** Creating a new microservice that needs environment-specific configuration for Kafka, AWS, and service metadata. This is the foundational pattern for all Fetch services.

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
        extra="ignore",  # Ignore extra env vars not in Settings
    )

    # Service metadata
    service_name: str = Field(default="my-service")
    version: str = Field(default="0.1.0")
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")

    # Server configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # AWS configuration
    aws_region: str = Field(default="us-east-1")
    aws_profile: str | None = Field(default=None)

    # Kafka configuration
    kafka_brokers: str = Field(default="localhost:9092")
    kafka_topic: str  # Required field, no default
    kafka_consumer_group: str  # Required field, no default
    use_msk_iam: bool = Field(default=False)

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str | None = Field(default=None)

    @field_validator("kafka_brokers")
    @classmethod
    def validate_kafka_brokers(cls, v: str) -> str:
        """Ensure Kafka brokers are properly formatted."""
        if not v:
            raise ValueError("kafka_brokers cannot be empty")
        return v

    @property
    def kafka_broker_list(self) -> list[str]:
        """Get Kafka brokers as list."""
        return [b.strip() for b in self.kafka_brokers.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# src/main.py
from src.config import get_settings

settings = get_settings()
print(f"Starting {settings.service_name} in {settings.environment}")
print(f"Connecting to Kafka: {settings.kafka_broker_list}")
```

**Environment file (.env) for local development:**
```bash
# .env
SERVICE_NAME=user-service
ENVIRONMENT=dev
LOG_LEVEL=DEBUG

# Kafka
KAFKA_TOPIC=user-events
KAFKA_CONSUMER_GROUP=user-service-consumer

# AWS
AWS_PROFILE=fetch-dev
```

**FSD automatically provides these in stage/prod:**
```bash
ENVIRONMENT=prod
AWS_REGION=us-east-1
KAFKA_BROKERS=b-1.prod-msk.kafka.us-east-1.amazonaws.com:9092,b-2.prod-msk.kafka.us-east-1.amazonaws.com:9092
USE_MSK_IAM=true
```

**Pitfalls:**
- **Forgetting required fields**: `kafka_topic` and `kafka_consumer_group` have no defaults and will cause ValidationError if not provided. This is intentional - these must be explicitly configured per service.
- **Case sensitivity**: Always set `case_sensitive=False` to handle both `KAFKA_TOPIC` and `kafka_topic` environment variables.
- **Not using @lru_cache**: Without caching, Settings is re-instantiated on every `get_settings()` call, causing performance overhead.

---

## Pattern 2: Nested Settings Configuration

**When to Use:** Managing complex configuration with logical grouping (database settings, cache settings, external APIs). This pattern improves organization when you have 20+ configuration values.

```python
# src/config.py
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",  # DB_HOST, DB_PORT, etc.
        case_sensitive=False,
    )

    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(default="mydb")
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    pool_size: int = Field(default=10, ge=1, le=100)
    pool_timeout: int = Field(default=30, ge=1)

    @property
    def url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",  # REDIS_HOST, REDIS_PORT, etc.
        case_sensitive=False,
    )

    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0, le=15)
    password: str | None = Field(default=None)
    ttl: int = Field(default=3600, ge=1)  # seconds

    @property
    def url(self) -> str:
        """Construct Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class KafkaSettings(BaseSettings):
    """Kafka streaming configuration."""

    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        case_sensitive=False,
    )

    brokers: str = Field(default="localhost:9092")
    topic: str  # Required
    consumer_group: str  # Required
    use_msk_iam: bool = Field(default=False)
    auto_offset_reset: Literal["earliest", "latest"] = Field(default="latest")

    @property
    def broker_list(self) -> list[str]:
        return [b.strip() for b in self.brokers.split(",")]


class Settings(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Service metadata
    service_name: str = Field(default="my-service")
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Usage
settings = get_settings()
print(f"Database: {settings.database.url}")
print(f"Redis: {settings.redis.url}")
print(f"Kafka brokers: {settings.kafka.broker_list}")
```

**Environment file (.env):**
```bash
# Service
SERVICE_NAME=data-processor
ENVIRONMENT=dev

# Database (DB_ prefix)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fetch_db
DB_USER=fetch_user
DB_PASSWORD=secret123
DB_POOL_SIZE=20

# Redis (REDIS_ prefix)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_secret
REDIS_TTL=7200

# Kafka (KAFKA_ prefix)
KAFKA_TOPIC=user-events
KAFKA_CONSUMER_GROUP=data-processor
```

**Pitfalls:**
- **Missing env_prefix**: Without `env_prefix`, nested settings will try to read `HOST` instead of `DB_HOST`, causing conflicts when multiple services need host configuration.
- **Forgetting default_factory**: Use `Field(default_factory=DatabaseSettings)` not `Field(default=DatabaseSettings())` to avoid sharing instances.
- **Circular dependencies**: Don't reference nested settings during initialization. Use properties or post-init validation instead.

---

## Pattern 3: Integration with AWS Secrets Manager

**When to Use:** Production services that need to load sensitive values (database passwords, API keys) from AWS Secrets Manager instead of environment variables. This pattern separates secret management from regular configuration.

```python
# src/config.py
import json
from functools import lru_cache
from typing import Any, Literal

import boto3
from botocore.exceptions import ClientError
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_secret(secret_name: str, region: str = "us-east-1") -> dict[str, Any]:
    """Load secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise ValueError(f"Secret {secret_name} not found") from e
        raise


class Settings(BaseSettings):
    """Application configuration with AWS Secrets Manager integration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Service metadata
    service_name: str = Field(default="my-service")
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")

    # AWS configuration
    aws_region: str = Field(default="us-east-1")
    aws_profile: str | None = Field(default=None)

    # Secret management
    secret_name: str | None = Field(default=None)
    use_secrets_manager: bool = Field(default=False)

    # Database (public config)
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = Field(default="mydb")

    # Database (secrets - loaded from Secrets Manager or env vars)
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="postgres")

    # API keys (secrets)
    external_api_key: str | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Load secrets after model initialization."""
        if self.use_secrets_manager and self.secret_name:
            self._load_secrets()

    def _load_secrets(self) -> None:
        """Load secrets from AWS Secrets Manager and update fields."""
        secret_data = load_secret(self.secret_name, self.aws_region)

        # Map secret keys to Settings fields
        if "db_user" in secret_data:
            self.db_user = secret_data["db_user"]
        if "db_password" in secret_data:
            self.db_password = secret_data["db_password"]
        if "external_api_key" in secret_data:
            self.external_api_key = secret_data["external_api_key"]

    @property
    def database_url(self) -> str:
        """Construct database URL with secrets."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# src/main.py
from src.config import get_settings

settings = get_settings()

# In production, db_user and db_password are loaded from Secrets Manager
# In dev, they use defaults from .env
print(f"Database: {settings.database_url}")
```

**Local development (.env):**
```bash
# Service
SERVICE_NAME=user-service
ENVIRONMENT=dev
USE_SECRETS_MANAGER=false

# Database (all from env vars in dev)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fetch_db
DB_USER=fetch_user
DB_PASSWORD=local_password
```

**Production environment (FSD provides):**
```bash
# Service
SERVICE_NAME=user-service
ENVIRONMENT=prod
USE_SECRETS_MANAGER=true
SECRET_NAME=prod/user-service/db-credentials
AWS_REGION=us-east-1

# Database (public config)
DB_HOST=prod-db.cluster-abc123.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=fetch_prod

# Secrets loaded from AWS Secrets Manager:
# - db_user
# - db_password
# - external_api_key
```

**AWS Secret structure (prod/user-service/db-credentials):**
```json
{
  "db_user": "prod_user",
  "db_password": "super_secure_password_123",
  "external_api_key": "sk-1234567890abcdef"
}
```

**Pitfalls:**
- **Caching secrets too early**: Don't load secrets in `__init__` or class body. Use `model_post_init` to ensure all env vars are loaded first.
- **Missing error handling**: Always handle `ClientError` when loading secrets. Services should fail fast with clear error messages if secrets are missing.
- **Exposing secrets in logs**: Never log Settings objects directly. Use `repr=False` in Field for sensitive values: `db_password: str = Field(repr=False)`.
- **Dev/prod inconsistency**: Test secret loading in stage environment before deploying to prod. Don't skip Secrets Manager in dev if prod uses it.

---

## Additional Patterns

### Environment-Specific Validation

Add stricter validation for production environments:

```python
from pydantic import model_validator

class Settings(BaseSettings):
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")
    external_api_key: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_production_requirements(self) -> "Settings":
        """Enforce strict validation in production."""
        if self.environment == "prod":
            if not self.external_api_key:
                raise ValueError("external_api_key is required in production")
            if self.log_level == "DEBUG":
                raise ValueError("DEBUG logging not allowed in production")
        return self
```

### FSD Environment Variable Conventions

Common FSD-provided environment variables in Fetch services:

```python
class Settings(BaseSettings):
    # FSD provides these automatically in deployed environments
    environment: Literal["dev", "stage", "preprod", "prod"] = Field(default="dev")
    aws_region: str = Field(default="us-east-1")

    # Kafka (FSD sets broker URLs for MSK)
    kafka_brokers: str = Field(default="localhost:9092")
    use_msk_iam: bool = Field(default=False)

    # Service mesh / networking
    service_name: str = Field(default="my-service")
    service_port: int = Field(default=8000)

    # Observability
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    dd_agent_host: str | None = Field(default=None)  # Datadog
```


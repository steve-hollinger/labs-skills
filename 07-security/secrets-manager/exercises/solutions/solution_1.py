"""Solution 1: Configuration Manager.

This solution demonstrates how to build a typed configuration loader
that retrieves and validates configuration from AWS Secrets Manager.
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

from botocore.exceptions import ClientError
from pydantic import BaseModel, ValidationError


class DatabaseConfig(BaseModel):
    """Database configuration with validation."""

    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    ssl_mode: str = "require"


class APIConfig(BaseModel):
    """External API configuration with validation."""

    api_key: str
    api_secret: str | None = None
    base_url: str
    timeout_seconds: int = 30


T = TypeVar("T", bound=BaseModel)


class ConfigurationManager:
    """Manages application configuration from Secrets Manager."""

    def __init__(self, client: Any, prefix: str = ""):
        """Initialize with Secrets Manager client and optional prefix.

        Args:
            client: boto3 secretsmanager client
            prefix: Optional prefix for all secret names (e.g., "myapp")
        """
        self.client = client
        self.prefix = prefix.rstrip("/") if prefix else ""

    def _get_full_name(self, secret_name: str) -> str:
        """Get the full secret name with prefix.

        Args:
            secret_name: The base secret name

        Returns:
            Full secret name with prefix
        """
        if self.prefix:
            return f"{self.prefix}/{secret_name}"
        return secret_name

    def _load_secret(self, secret_name: str) -> dict[str, Any]:
        """Load a secret and parse as JSON.

        Args:
            secret_name: The secret name

        Returns:
            Parsed JSON data

        Raises:
            KeyError: If secret not found
            ValueError: If secret is not valid JSON
        """
        full_name = self._get_full_name(secret_name)

        try:
            response = self.client.get_secret_value(SecretId=full_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise KeyError(f"Secret not found: {full_name}") from e
            raise

        secret_string = response.get("SecretString")
        if not secret_string:
            raise ValueError(f"Secret {full_name} has no string value")

        try:
            return json.loads(secret_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Secret {full_name} is not valid JSON: {e}") from e

    def _load_config(self, secret_name: str, schema: type[T]) -> T:
        """Load and validate configuration against a schema.

        Args:
            secret_name: The secret name
            schema: Pydantic model class for validation

        Returns:
            Validated configuration object

        Raises:
            KeyError: If secret not found
            ValueError: If validation fails
        """
        data = self._load_secret(secret_name)

        try:
            return schema.model_validate(data)
        except ValidationError as e:
            full_name = self._get_full_name(secret_name)
            # Don't expose secret values in error messages
            field_errors = [
                f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
            ]
            raise ValueError(
                f"Configuration validation failed for {full_name}: "
                f"{'; '.join(field_errors)}"
            ) from e

    def get_database_config(self, secret_name: str) -> DatabaseConfig:
        """Load and validate database configuration.

        Args:
            secret_name: Name of the secret containing database config

        Returns:
            Validated DatabaseConfig object

        Raises:
            KeyError: If secret not found
            ValueError: If validation fails
        """
        return self._load_config(secret_name, DatabaseConfig)

    def get_api_config(self, secret_name: str) -> APIConfig:
        """Load and validate API configuration.

        Args:
            secret_name: Name of the secret containing API config

        Returns:
            Validated APIConfig object

        Raises:
            KeyError: If secret not found
            ValueError: If validation fails
        """
        return self._load_config(secret_name, APIConfig)


def main() -> None:
    """Demonstrate the ConfigurationManager."""
    import os

    from secrets_manager import get_secrets_client

    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Solution 1: Configuration Manager")
    print("=" * 60)

    client = get_secrets_client(use_localstack=True)

    # Clean up previous runs
    for name in ["test/database", "test/api"]:
        try:
            client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
        except Exception:
            pass

    # Create test secrets
    print("\n1. Creating test secrets...")
    client.create_secret(
        Name="test/database",
        SecretString=json.dumps({
            "host": "db.example.com",
            "port": 5432,
            "database": "myapp",
            "username": "app_user",
            "password": "super-secret-password",
        }),
    )
    client.create_secret(
        Name="test/api",
        SecretString=json.dumps({
            "api_key": "sk_example_FAKE",
            "api_secret": "secret_xyz789",
            "base_url": "https://api.example.com/v1",
            "timeout_seconds": 60,
        }),
    )
    print("   Created test/database and test/api")

    # Use ConfigurationManager
    print("\n2. Loading configurations with prefix...")
    manager = ConfigurationManager(client, prefix="test")

    db_config = manager.get_database_config("database")
    print(f"   Database: {db_config.host}:{db_config.port}/{db_config.database}")
    print(f"   Username: {db_config.username}")
    print(f"   SSL Mode: {db_config.ssl_mode}")

    api_config = manager.get_api_config("api")
    print(f"\n   API Base URL: {api_config.base_url}")
    print(f"   Timeout: {api_config.timeout_seconds}s")

    # Test error handling
    print("\n3. Testing error handling...")
    try:
        manager.get_database_config("nonexistent")
    except KeyError as e:
        print(f"   Missing secret handled: {e}")

    # Test validation error
    print("\n4. Testing validation error...")
    client.create_secret(
        Name="test/invalid-db",
        SecretString=json.dumps({
            "host": "localhost",
            # Missing required fields
        }),
    )
    manager_no_prefix = ConfigurationManager(client)
    try:
        manager_no_prefix.get_database_config("test/invalid-db")
    except ValueError as e:
        print(f"   Validation error handled: {e}")

    # Clean up
    print("\n5. Cleaning up...")
    for name in ["test/database", "test/api", "test/invalid-db"]:
        try:
            client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("Solution 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

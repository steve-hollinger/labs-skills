"""Exercise 1: Configuration Manager.

Create a ConfigurationManager class that loads application configuration
from AWS Secrets Manager with the following requirements:

1. Load database configuration from a secret
2. Load API credentials from another secret
3. Validate the configuration using Pydantic
4. Raise helpful errors for missing or invalid config

Expected usage:
    manager = ConfigurationManager(client)
    db_config = manager.get_database_config("myapp/database")
    api_config = manager.get_api_config("myapp/external-api")

Hints:
- Use Pydantic BaseModel for validation
- Handle ResourceNotFoundException gracefully
- Parse JSON secrets into typed objects
"""

from __future__ import annotations

from typing import Any

# TODO: Import necessary modules
# from pydantic import BaseModel


class DatabaseConfig:
    """Database configuration.

    TODO: Convert to Pydantic model with fields:
    - host: str
    - port: int (default 5432)
    - database: str
    - username: str
    - password: str
    - ssl_mode: str (default "require")
    """

    pass


class APIConfig:
    """External API configuration.

    TODO: Convert to Pydantic model with fields:
    - api_key: str
    - api_secret: str (optional)
    - base_url: str
    - timeout_seconds: int (default 30)
    """

    pass


class ConfigurationManager:
    """Manages application configuration from Secrets Manager.

    TODO: Implement this class with:
    - __init__(self, client, prefix: str = "")
    - get_database_config(self, secret_name: str) -> DatabaseConfig
    - get_api_config(self, secret_name: str) -> APIConfig
    """

    def __init__(self, client: Any, prefix: str = ""):
        """Initialize with Secrets Manager client and optional prefix.

        Args:
            client: boto3 secretsmanager client
            prefix: Optional prefix for all secret names
        """
        # TODO: Store client and prefix
        pass

    def get_database_config(self, secret_name: str) -> DatabaseConfig:
        """Load and validate database configuration.

        Args:
            secret_name: Name of the secret containing database config

        Returns:
            Validated DatabaseConfig object

        Raises:
            KeyError: If secret not found
            ValidationError: If secret doesn't match schema
        """
        # TODO: Implement this method
        raise NotImplementedError("Implement get_database_config")

    def get_api_config(self, secret_name: str) -> APIConfig:
        """Load and validate API configuration.

        Args:
            secret_name: Name of the secret containing API config

        Returns:
            Validated APIConfig object

        Raises:
            KeyError: If secret not found
            ValidationError: If secret doesn't match schema
        """
        # TODO: Implement this method
        raise NotImplementedError("Implement get_api_config")


def main() -> None:
    """Test your implementation."""
    # This will be used to test your implementation
    # Uncomment after implementing the classes

    # from secrets_manager import get_secrets_client
    # import os
    # os.environ.setdefault("USE_LOCALSTACK", "1")
    #
    # client = get_secrets_client(use_localstack=True)
    #
    # # Create test secrets
    # import json
    # client.create_secret(
    #     Name="test/database",
    #     SecretString=json.dumps({
    #         "host": "localhost",
    #         "port": 5432,
    #         "database": "testdb",
    #         "username": "user",
    #         "password": "pass"
    #     })
    # )
    #
    # # Test your implementation
    # manager = ConfigurationManager(client)
    # db_config = manager.get_database_config("test/database")
    # print(f"Database host: {db_config.host}")
    # print(f"Database port: {db_config.port}")

    print("Exercise 1: Implement ConfigurationManager")
    print("See the solution in solutions/solution_1.py")


if __name__ == "__main__":
    main()

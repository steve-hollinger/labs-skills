"""AWS Secrets Manager skill module.

This module provides utilities for working with AWS Secrets Manager,
including local development support with LocalStack.
"""

from secrets_manager.client import (
    SecretCache,
    SecretsClient,
    create_secret,
    delete_secret,
    get_secret,
    get_secrets_client,
    list_secrets,
    update_secret,
)

__all__ = [
    "SecretsClient",
    "SecretCache",
    "get_secrets_client",
    "get_secret",
    "create_secret",
    "update_secret",
    "delete_secret",
    "list_secrets",
]

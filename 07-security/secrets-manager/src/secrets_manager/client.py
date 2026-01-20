"""AWS Secrets Manager client utilities.

This module provides a wrapper around boto3's secretsmanager client
with support for LocalStack and caching.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError


def get_secrets_client(use_localstack: bool | None = None) -> BaseClient:
    """Get a Secrets Manager client.

    Args:
        use_localstack: If True, connect to LocalStack. If None, auto-detect
                       from LOCALSTACK_URL or USE_LOCALSTACK environment variables.

    Returns:
        A boto3 secretsmanager client.
    """
    if use_localstack is None:
        use_localstack = bool(
            os.environ.get("LOCALSTACK_URL") or os.environ.get("USE_LOCALSTACK")
        )

    if use_localstack:
        endpoint_url = os.environ.get("LOCALSTACK_URL", "http://localhost:4566")
        return boto3.client(
            "secretsmanager",
            endpoint_url=endpoint_url,
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )

    return boto3.client(
        "secretsmanager",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def get_secret(
    client: BaseClient,
    secret_name: str,
    version_stage: str = "AWSCURRENT",
) -> dict[str, Any] | str | None:
    """Retrieve a secret from Secrets Manager.

    Args:
        client: The boto3 secretsmanager client.
        secret_name: The name or ARN of the secret.
        version_stage: The version stage (default: AWSCURRENT).

    Returns:
        The secret value as a dict (if JSON) or string, or None if not found.

    Raises:
        ClientError: If an error occurs other than ResourceNotFoundException.
    """
    try:
        response = client.get_secret_value(
            SecretId=secret_name,
            VersionStage=version_stage,
        )

        if "SecretString" in response:
            secret_string = response["SecretString"]
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError:
                return secret_string

        # Binary secret
        return response.get("SecretBinary")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        raise


def create_secret(
    client: BaseClient,
    name: str,
    value: dict[str, Any] | str,
    description: str = "",
    tags: dict[str, str] | None = None,
) -> str:
    """Create a new secret.

    Args:
        client: The boto3 secretsmanager client.
        name: The name for the secret.
        value: The secret value (dict will be JSON-encoded).
        description: Optional description.
        tags: Optional tags as key-value pairs.

    Returns:
        The ARN of the created secret.
    """
    secret_string = json.dumps(value) if isinstance(value, dict) else value

    kwargs: dict[str, Any] = {
        "Name": name,
        "SecretString": secret_string,
    }

    if description:
        kwargs["Description"] = description

    if tags:
        kwargs["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

    response = client.create_secret(**kwargs)
    return response["ARN"]


def update_secret(
    client: BaseClient,
    name: str,
    value: dict[str, Any] | str,
) -> str:
    """Update an existing secret.

    Args:
        client: The boto3 secretsmanager client.
        name: The name or ARN of the secret.
        value: The new secret value.

    Returns:
        The ARN of the updated secret.
    """
    secret_string = json.dumps(value) if isinstance(value, dict) else value

    response = client.update_secret(
        SecretId=name,
        SecretString=secret_string,
    )
    return response["ARN"]


def delete_secret(
    client: BaseClient,
    name: str,
    force: bool = False,
    recovery_days: int = 30,
) -> None:
    """Delete a secret.

    Args:
        client: The boto3 secretsmanager client.
        name: The name or ARN of the secret.
        force: If True, delete immediately without recovery window.
        recovery_days: Days to retain secret before permanent deletion (7-30).
    """
    kwargs: dict[str, Any] = {"SecretId": name}

    if force:
        kwargs["ForceDeleteWithoutRecovery"] = True
    else:
        kwargs["RecoveryWindowInDays"] = recovery_days

    client.delete_secret(**kwargs)


def list_secrets(
    client: BaseClient,
    name_prefix: str | None = None,
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List secrets, optionally filtered by name prefix.

    Args:
        client: The boto3 secretsmanager client.
        name_prefix: Optional prefix to filter secret names.
        max_results: Maximum number of results to return.

    Returns:
        List of secret metadata dictionaries.
    """
    kwargs: dict[str, Any] = {"MaxResults": min(max_results, 100)}

    if name_prefix:
        kwargs["Filters"] = [{"Key": "name", "Values": [name_prefix]}]

    secrets = []
    paginator = client.get_paginator("list_secrets")

    for page in paginator.paginate(**kwargs):
        secrets.extend(page.get("SecretList", []))
        if len(secrets) >= max_results:
            break

    return secrets[:max_results]


@dataclass
class CachedSecret:
    """A cached secret with expiration time."""

    value: Any
    expires_at: float
    version_id: str | None = None


@dataclass
class SecretCache:
    """Thread-safe secret cache with TTL expiration.

    Example:
        cache = SecretCache(ttl_seconds=300)
        secret = cache.get("myapp/database")
    """

    client: BaseClient | None = None
    ttl_seconds: int = 300
    refresh_before_expiry: int = 60
    _cache: dict[str, CachedSecret] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = get_secrets_client()

    def get(
        self,
        secret_name: str,
        force_refresh: bool = False,
    ) -> dict[str, Any] | str | None:
        """Get a secret, using cache if valid.

        Args:
            secret_name: The name or ARN of the secret.
            force_refresh: If True, bypass cache and fetch fresh.

        Returns:
            The secret value or None if not found.
        """
        now = time.time()

        with self._lock:
            if not force_refresh and secret_name in self._cache:
                cached = self._cache[secret_name]
                if now < cached.expires_at - self.refresh_before_expiry:
                    return cached.value

        # Fetch from Secrets Manager
        assert self.client is not None
        value = get_secret(self.client, secret_name)

        with self._lock:
            self._cache[secret_name] = CachedSecret(
                value=value,
                expires_at=now + self.ttl_seconds,
            )

        return value

    def invalidate(self, secret_name: str | None = None) -> None:
        """Invalidate cache entries.

        Args:
            secret_name: Specific secret to invalidate, or None for all.
        """
        with self._lock:
            if secret_name:
                self._cache.pop(secret_name, None)
            else:
                self._cache.clear()


class SecretsClient:
    """High-level Secrets Manager client with caching support.

    Example:
        client = SecretsClient(use_localstack=True)
        client.create("myapp/database", {"user": "admin", "pass": "secret"})
        config = client.get("myapp/database")
    """

    def __init__(
        self,
        use_localstack: bool | None = None,
        cache_ttl: int = 300,
        enable_cache: bool = True,
    ):
        """Initialize the client.

        Args:
            use_localstack: If True, connect to LocalStack.
            cache_ttl: Cache TTL in seconds (default 300).
            enable_cache: If True, enable caching (default True).
        """
        self._client = get_secrets_client(use_localstack)
        self._enable_cache = enable_cache
        self._cache = SecretCache(
            client=self._client,
            ttl_seconds=cache_ttl,
        ) if enable_cache else None

    def get(
        self,
        name: str,
        force_refresh: bool = False,
    ) -> dict[str, Any] | str | None:
        """Get a secret value.

        Args:
            name: The secret name or ARN.
            force_refresh: Bypass cache if enabled.

        Returns:
            The secret value or None if not found.
        """
        if self._cache and not force_refresh:
            return self._cache.get(name)
        return get_secret(self._client, name)

    def create(
        self,
        name: str,
        value: dict[str, Any] | str,
        description: str = "",
        tags: dict[str, str] | None = None,
    ) -> str:
        """Create a new secret.

        Args:
            name: The secret name.
            value: The secret value.
            description: Optional description.
            tags: Optional tags.

        Returns:
            The ARN of the created secret.
        """
        arn = create_secret(self._client, name, value, description, tags)
        if self._cache:
            self._cache.invalidate(name)
        return arn

    def update(self, name: str, value: dict[str, Any] | str) -> str:
        """Update an existing secret.

        Args:
            name: The secret name or ARN.
            value: The new secret value.

        Returns:
            The ARN of the updated secret.
        """
        arn = update_secret(self._client, name, value)
        if self._cache:
            self._cache.invalidate(name)
        return arn

    def delete(
        self,
        name: str,
        force: bool = False,
        recovery_days: int = 30,
    ) -> None:
        """Delete a secret.

        Args:
            name: The secret name or ARN.
            force: If True, delete immediately.
            recovery_days: Days before permanent deletion.
        """
        delete_secret(self._client, name, force, recovery_days)
        if self._cache:
            self._cache.invalidate(name)

    def list(
        self,
        name_prefix: str | None = None,
        max_results: int = 100,
    ) -> list[dict[str, Any]]:
        """List secrets.

        Args:
            name_prefix: Optional name prefix filter.
            max_results: Maximum results to return.

        Returns:
            List of secret metadata.
        """
        return list_secrets(self._client, name_prefix, max_results)

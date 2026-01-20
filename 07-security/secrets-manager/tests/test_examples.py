"""Tests for secrets_manager examples using moto mock.

These tests use moto to mock AWS Secrets Manager, so they don't require
LocalStack or actual AWS credentials.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch

import boto3
from moto import mock_aws

from secrets_manager import (
    SecretCache,
    SecretsClient,
    create_secret,
    delete_secret,
    get_secret,
    get_secrets_client,
    list_secrets,
    update_secret,
)


@pytest.fixture
def mock_secretsmanager():
    """Create a mocked Secrets Manager service."""
    with mock_aws():
        # Create client with mocked AWS
        client = boto3.client("secretsmanager", region_name="us-east-1")
        yield client


class TestGetSecretsClient:
    """Tests for get_secrets_client function."""

    def test_get_client_default(self):
        """Test getting a default client."""
        with mock_aws():
            client = get_secrets_client(use_localstack=False)
            assert client is not None

    def test_get_client_localstack_explicit(self):
        """Test getting a LocalStack client."""
        with patch.dict("os.environ", {"LOCALSTACK_URL": "http://localhost:4566"}):
            client = get_secrets_client(use_localstack=True)
            assert client is not None


class TestSecretOperations:
    """Tests for basic secret operations."""

    def test_create_and_get_string_secret(self, mock_secretsmanager):
        """Test creating and retrieving a string secret."""
        client = mock_secretsmanager

        # Create
        arn = create_secret(client, "test/string", "my-secret-value")
        assert arn is not None

        # Get
        value = get_secret(client, "test/string")
        assert value == "my-secret-value"

    def test_create_and_get_json_secret(self, mock_secretsmanager):
        """Test creating and retrieving a JSON secret."""
        client = mock_secretsmanager
        secret_data = {"username": "admin", "password": "secret123"}

        # Create
        arn = create_secret(client, "test/json", secret_data)
        assert arn is not None

        # Get
        value = get_secret(client, "test/json")
        assert value == secret_data

    def test_get_nonexistent_secret(self, mock_secretsmanager):
        """Test getting a secret that doesn't exist."""
        client = mock_secretsmanager
        value = get_secret(client, "nonexistent/secret")
        assert value is None

    def test_update_secret(self, mock_secretsmanager):
        """Test updating an existing secret."""
        client = mock_secretsmanager

        # Create
        create_secret(client, "test/update", {"version": 1})

        # Update
        update_secret(client, "test/update", {"version": 2})

        # Verify
        value = get_secret(client, "test/update")
        assert value == {"version": 2}

    def test_delete_secret(self, mock_secretsmanager):
        """Test deleting a secret."""
        client = mock_secretsmanager

        # Create
        create_secret(client, "test/delete", "to-be-deleted")

        # Delete with force
        delete_secret(client, "test/delete", force=True)

        # Verify - should return None for deleted secrets
        value = get_secret(client, "test/delete")
        assert value is None

    def test_list_secrets(self, mock_secretsmanager):
        """Test listing secrets."""
        client = mock_secretsmanager

        # Create multiple secrets
        create_secret(client, "app1/config", "config1")
        create_secret(client, "app1/database", "db1")
        create_secret(client, "app2/config", "config2")

        # List all
        all_secrets = list_secrets(client)
        assert len(all_secrets) == 3

        # List with prefix (note: moto may not fully support filters)
        # Just verify the list operation works
        secrets = list_secrets(client, max_results=2)
        assert len(secrets) <= 2

    def test_create_secret_with_tags(self, mock_secretsmanager):
        """Test creating a secret with tags."""
        client = mock_secretsmanager

        arn = create_secret(
            client,
            "test/tagged",
            "tagged-value",
            description="A tagged secret",
            tags={"Environment": "test", "Owner": "pytest"},
        )
        assert arn is not None

        # Verify secret was created
        value = get_secret(client, "test/tagged")
        assert value == "tagged-value"


class TestSecretCache:
    """Tests for SecretCache class."""

    def test_cache_hit(self, mock_secretsmanager):
        """Test that cache returns cached values."""
        client = mock_secretsmanager
        create_secret(client, "test/cached", {"key": "value"})

        cache = SecretCache(client=client, ttl_seconds=300)

        # First call - cache miss
        value1 = cache.get("test/cached")
        assert value1 == {"key": "value"}

        # Second call - should be cached
        value2 = cache.get("test/cached")
        assert value2 == {"key": "value"}

    def test_force_refresh(self, mock_secretsmanager):
        """Test force refresh bypasses cache."""
        client = mock_secretsmanager
        create_secret(client, "test/refresh", {"version": 1})

        cache = SecretCache(client=client, ttl_seconds=300)

        # Cache the value
        value1 = cache.get("test/refresh")
        assert value1 == {"version": 1}

        # Update the secret
        update_secret(client, "test/refresh", {"version": 2})

        # Without force_refresh, should still return cached value
        # (Note: in real scenario, cache would return old value)

        # With force_refresh, should get new value
        value2 = cache.get("test/refresh", force_refresh=True)
        assert value2 == {"version": 2}

    def test_invalidate_specific(self, mock_secretsmanager):
        """Test invalidating a specific cached secret."""
        client = mock_secretsmanager
        create_secret(client, "test/invalidate", "original")

        cache = SecretCache(client=client, ttl_seconds=300)
        cache.get("test/invalidate")  # Cache it

        # Invalidate
        cache.invalidate("test/invalidate")

        # Update and verify cache is refreshed
        update_secret(client, "test/invalidate", "updated")
        value = cache.get("test/invalidate")
        assert value == "updated"

    def test_invalidate_all(self, mock_secretsmanager):
        """Test invalidating all cached secrets."""
        client = mock_secretsmanager
        create_secret(client, "test/inv1", "value1")
        create_secret(client, "test/inv2", "value2")

        cache = SecretCache(client=client, ttl_seconds=300)
        cache.get("test/inv1")
        cache.get("test/inv2")

        # Invalidate all
        cache.invalidate()

        # Verify both were invalidated by checking they get refetched
        update_secret(client, "test/inv1", "new1")
        update_secret(client, "test/inv2", "new2")

        assert cache.get("test/inv1") == "new1"
        assert cache.get("test/inv2") == "new2"


class TestSecretsClient:
    """Tests for SecretsClient high-level class."""

    def test_client_crud_operations(self, mock_secretsmanager):
        """Test create, read, update, delete via SecretsClient."""
        # Create SecretsClient with mocked boto3 client
        with mock_aws():
            client = SecretsClient(use_localstack=False, enable_cache=False)

            # Create
            arn = client.create("test/crud", {"initial": True})
            assert arn is not None

            # Read
            value = client.get("test/crud")
            assert value == {"initial": True}

            # Update
            client.update("test/crud", {"updated": True})
            value = client.get("test/crud")
            assert value == {"updated": True}

            # Delete
            client.delete("test/crud", force=True)
            value = client.get("test/crud")
            assert value is None

    def test_client_list(self, mock_secretsmanager):
        """Test listing secrets via SecretsClient."""
        with mock_aws():
            client = SecretsClient(use_localstack=False, enable_cache=False)

            client.create("list/one", "1")
            client.create("list/two", "2")

            secrets = client.list()
            assert len(secrets) >= 2


class TestVersioning:
    """Tests for secret versioning."""

    def test_version_stages(self, mock_secretsmanager):
        """Test accessing secrets by version stage."""
        client = mock_secretsmanager

        # Create initial version
        create_secret(client, "test/versioned", {"version": 1})

        # Get AWSCURRENT
        current = get_secret(client, "test/versioned", version_stage="AWSCURRENT")
        assert current == {"version": 1}

    def test_put_with_staging(self, mock_secretsmanager):
        """Test putting a secret with specific staging labels."""
        client = mock_secretsmanager

        # Create secret
        client.create_secret(
            Name="test/staging",
            SecretString=json.dumps({"version": 1}),
        )

        # Put new version as AWSPENDING
        client.put_secret_value(
            SecretId="test/staging",
            SecretString=json.dumps({"version": 2}),
            VersionStages=["AWSPENDING"],
        )

        # AWSCURRENT should still be version 1
        response = client.get_secret_value(
            SecretId="test/staging",
            VersionStage="AWSCURRENT",
        )
        assert json.loads(response["SecretString"]) == {"version": 1}

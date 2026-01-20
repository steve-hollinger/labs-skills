"""Example 2: JSON Secrets with Versioning and Caching.

This example demonstrates advanced secret operations:
- Storing structured JSON secrets
- Working with secret versions
- Using the caching layer
- Accessing specific versions

Run with: make example-2
Requires: LocalStack running (make localstack-up)
"""

from __future__ import annotations

import json
import os
import time

import boto3

from secrets_manager import SecretCache, get_secrets_client


def main() -> None:
    """Demonstrate JSON secrets, versioning, and caching."""
    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Example 2: JSON Secrets with Versioning and Caching")
    print("=" * 60)

    # Get the low-level client for version operations
    client = get_secrets_client(use_localstack=True)
    secret_name = "example/database-config"

    # Clean up from previous runs
    try:
        client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
        time.sleep(1)  # Allow time for deletion
    except Exception:
        pass

    # 1. Create a JSON secret (database configuration)
    print("\n1. Creating a database configuration secret...")
    db_config_v1 = {
        "host": "db-old.example.com",
        "port": 5432,
        "database": "myapp",
        "username": "app_user",
        "password": "old-password-123",
        "ssl_mode": "require",
    }

    response = client.create_secret(
        Name=secret_name,
        SecretString=json.dumps(db_config_v1),
        Description="Database connection configuration",
    )
    print(f"   Created secret ARN: {response['ARN']}")

    # 2. Retrieve and parse JSON secret
    print("\n2. Retrieving JSON secret...")
    response = client.get_secret_value(SecretId=secret_name)
    config = json.loads(response["SecretString"])
    print(f"   Host: {config['host']}")
    print(f"   Database: {config['database']}")
    print(f"   Username: {config['username']}")
    print(f"   Password: {'*' * len(config['password'])} (masked)")

    # 3. Update the secret (creates a new version)
    print("\n3. Updating secret (creates new version)...")
    db_config_v2 = {
        **db_config_v1,
        "host": "db-new.example.com",
        "password": "new-password-456",
    }
    client.update_secret(
        SecretId=secret_name,
        SecretString=json.dumps(db_config_v2),
    )
    print("   Updated host and password")

    # 4. List versions
    print("\n4. Listing secret versions...")
    versions_response = client.list_secret_version_ids(SecretId=secret_name)
    for version in versions_response.get("Versions", []):
        stages = version.get("VersionStages", [])
        print(f"   Version: {version['VersionId'][:8]}...")
        print(f"   Stages: {stages}")
        print()

    # 5. Access current version explicitly
    print("5. Accessing AWSCURRENT version...")
    current = client.get_secret_value(
        SecretId=secret_name,
        VersionStage="AWSCURRENT",
    )
    current_config = json.loads(current["SecretString"])
    print(f"   Current host: {current_config['host']}")

    # 6. Demonstrate caching
    print("\n6. Demonstrating secret caching...")
    cache = SecretCache(client=client, ttl_seconds=60)

    print("   First fetch (from API):")
    start = time.time()
    cached_config = cache.get(secret_name)
    first_time = time.time() - start
    print(f"   Time: {first_time*1000:.2f}ms")
    print(f"   Host: {cached_config['host']}")

    print("\n   Second fetch (from cache):")
    start = time.time()
    cached_config = cache.get(secret_name)
    second_time = time.time() - start
    print(f"   Time: {second_time*1000:.2f}ms")
    print(f"   Host: {cached_config['host']}")

    if second_time < first_time:
        print(f"\n   Cache speedup: {first_time/max(second_time, 0.0001):.1f}x faster")

    # 7. Force refresh cache
    print("\n7. Force refreshing cache...")
    refreshed = cache.get(secret_name, force_refresh=True)
    print(f"   Refreshed host: {refreshed['host']}")

    # 8. Invalidate cache
    print("\n8. Invalidating cache...")
    cache.invalidate(secret_name)
    print("   Cache invalidated")

    # Clean up
    print("\n9. Cleaning up...")
    client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
    print(f"   Deleted: {secret_name}")

    print("\n" + "=" * 60)
    print("Example 2 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

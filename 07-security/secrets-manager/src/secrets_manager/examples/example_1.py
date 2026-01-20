"""Example 1: Basic Secret Storage and Retrieval.

This example demonstrates fundamental Secrets Manager operations:
- Creating secrets
- Retrieving secrets
- Updating secrets
- Deleting secrets

Run with: make example-1
Requires: LocalStack running (make localstack-up)
"""

from __future__ import annotations

import json
import os

from secrets_manager import SecretsClient


def main() -> None:
    """Demonstrate basic secret operations."""
    # Use LocalStack for local development
    # Set USE_LOCALSTACK=1 or LOCALSTACK_URL to enable
    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Example 1: Basic Secret Storage and Retrieval")
    print("=" * 60)

    # Create a client (automatically uses LocalStack if configured)
    client = SecretsClient(use_localstack=True, enable_cache=False)

    secret_name = "example/basic-secret"

    # Clean up from previous runs
    try:
        client.delete(secret_name, force=True)
    except Exception:
        pass

    # 1. Create a simple string secret
    print("\n1. Creating a simple string secret...")
    client.create(
        name=secret_name,
        value="my-super-secret-api-key",
        description="Example API key for demonstration",
        tags={"Environment": "development", "Owner": "example"},
    )
    print(f"   Created secret: {secret_name}")

    # 2. Retrieve the secret
    print("\n2. Retrieving the secret...")
    secret = client.get(secret_name)
    print(f"   Secret value: {secret}")

    # 3. Update with a JSON value
    print("\n3. Updating secret with JSON data...")
    json_secret = {
        "api_key": "new-api-key-12345",
        "api_secret": "corresponding-secret",
        "endpoint": "https://api.example.com",
    }
    client.update(secret_name, json_secret)
    print(f"   Updated with: {json.dumps(json_secret, indent=2)}")

    # 4. Retrieve the updated secret
    print("\n4. Retrieving updated secret...")
    updated_secret = client.get(secret_name)
    print(f"   Retrieved: {json.dumps(updated_secret, indent=2)}")

    # 5. List secrets
    print("\n5. Listing secrets with 'example/' prefix...")
    secrets = client.list(name_prefix="example/")
    for s in secrets:
        print(f"   - {s['Name']}")

    # 6. Delete the secret
    print("\n6. Deleting the secret...")
    client.delete(secret_name, force=True)
    print(f"   Deleted: {secret_name}")

    # 7. Verify deletion
    print("\n7. Verifying deletion...")
    deleted_secret = client.get(secret_name)
    if deleted_secret is None:
        print("   Secret successfully deleted (returns None)")
    else:
        print(f"   Unexpected: Secret still exists: {deleted_secret}")

    print("\n" + "=" * 60)
    print("Example 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

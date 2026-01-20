"""Example 3: Secret Rotation Patterns.

This example demonstrates secret rotation concepts:
- The 4-step rotation protocol
- Creating new secret versions
- Managing version stages (AWSCURRENT, AWSPENDING, AWSPREVIOUS)
- Implementing a rotation handler

Run with: make example-3
Requires: LocalStack running (make localstack-up)

Note: In production, rotation would be triggered by AWS Lambda.
This example simulates the rotation steps locally.
"""

from __future__ import annotations

import json
import os
import secrets
import string
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from secrets_manager import get_secrets_client


def generate_password(length: int = 32) -> str:
    """Generate a cryptographically secure password."""
    # Use letters, digits, and safe special characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))


class RotationHandler(ABC):
    """Base class for secret rotation handlers.

    This implements the AWS Secrets Manager rotation protocol:
    1. createSecret - Generate new credentials
    2. setSecret - Apply new credentials to the resource
    3. testSecret - Verify new credentials work
    4. finishSecret - Move version stages

    Subclasses must implement:
    - generate_new_secret()
    - apply_secret()
    - test_secret()
    """

    def __init__(self, client: Any):
        self.client = client

    def rotate(self, secret_id: str) -> None:
        """Perform a complete rotation.

        In production, AWS Lambda calls this for each step separately.
        Here we execute all steps sequentially for demonstration.
        """
        # Generate a unique token for this rotation
        token = str(uuid.uuid4())

        print(f"\n   Starting rotation for: {secret_id}")
        print(f"   Rotation token: {token[:8]}...")

        # Execute rotation steps
        self._create_secret(secret_id, token)
        self._set_secret(secret_id, token)
        self._test_secret(secret_id, token)
        self._finish_secret(secret_id, token)

        print("   Rotation complete!")

    def _create_secret(self, secret_id: str, token: str) -> None:
        """Step 1: Create new secret version with AWSPENDING stage."""
        print("\n   Step 1: createSecret")

        # Get current secret
        current = self.client.get_secret_value(
            SecretId=secret_id,
            VersionStage="AWSCURRENT",
        )
        current_secret = json.loads(current["SecretString"])
        print(f"      Current password: {current_secret['password'][:8]}...")

        # Generate new secret values
        new_secret = self.generate_new_secret(current_secret)
        print(f"      New password: {new_secret['password'][:8]}...")

        # Store as AWSPENDING
        self.client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps(new_secret),
            VersionStages=["AWSPENDING"],
        )
        print("      Stored new version as AWSPENDING")

    @abstractmethod
    def generate_new_secret(self, current: dict[str, Any]) -> dict[str, Any]:
        """Generate new secret values.

        Override this method to customize secret generation.
        """
        pass

    def _set_secret(self, secret_id: str, token: str) -> None:
        """Step 2: Apply new credentials to the resource."""
        print("\n   Step 2: setSecret")

        # Get pending secret
        pending = self.client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage="AWSPENDING",
        )
        secret = json.loads(pending["SecretString"])

        # Apply to the resource (database, API, etc.)
        self.apply_secret(secret)
        print("      Applied new credentials to resource")

    @abstractmethod
    def apply_secret(self, secret: dict[str, Any]) -> None:
        """Apply the new secret to the resource.

        Override this method to update your database, API, etc.
        """
        pass

    def _test_secret(self, secret_id: str, token: str) -> None:
        """Step 3: Verify new credentials work."""
        print("\n   Step 3: testSecret")

        # Get pending secret
        pending = self.client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage="AWSPENDING",
        )
        secret = json.loads(pending["SecretString"])

        # Test the new credentials
        self.test_secret(secret)
        print("      New credentials verified")

    @abstractmethod
    def test_secret(self, secret: dict[str, Any]) -> None:
        """Test that the new secret works.

        Override this method to verify connectivity.
        """
        pass

    def _finish_secret(self, secret_id: str, token: str) -> None:
        """Step 4: Move AWSCURRENT to new version."""
        print("\n   Step 4: finishSecret")

        # Get metadata to find current version
        metadata = self.client.describe_secret(SecretId=secret_id)

        current_version = None
        for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
            if "AWSCURRENT" in stages:
                current_version = version_id
                break

        if current_version == token:
            print("      Already current, skipping")
            return

        # Move AWSCURRENT to the new version
        # This automatically moves old AWSCURRENT to AWSPREVIOUS
        self.client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage="AWSCURRENT",
            MoveToVersionId=token,
            RemoveFromVersionId=current_version,
        )
        print(f"      Moved AWSCURRENT to new version")
        print(f"      Previous version: {current_version[:8]}... -> AWSPREVIOUS")


class DatabaseRotationHandler(RotationHandler):
    """Example rotation handler for database credentials.

    In a real implementation, this would:
    - Connect to the database
    - Update the user's password
    - Verify the new password works
    """

    def __init__(self, client: Any):
        super().__init__(client)
        # Simulated database state
        self._db_password: str | None = None

    def generate_new_secret(self, current: dict[str, Any]) -> dict[str, Any]:
        """Generate new database credentials."""
        return {
            **current,
            "password": generate_password(24),
            "rotated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def apply_secret(self, secret: dict[str, Any]) -> None:
        """Apply new password to the database.

        In production, this would execute:
        ALTER USER app_user WITH PASSWORD 'new_password';
        """
        # Simulate database password update
        self._db_password = secret["password"]
        print(f"      [Simulated] Updated database user: {secret['username']}")

    def test_secret(self, secret: dict[str, Any]) -> None:
        """Test database connection with new credentials.

        In production, this would attempt a real connection.
        """
        # Simulate connection test
        if self._db_password != secret["password"]:
            raise RuntimeError("Password mismatch - rotation failed")
        print(f"      [Simulated] Connection test passed")


def main() -> None:
    """Demonstrate secret rotation patterns."""
    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Example 3: Secret Rotation Patterns")
    print("=" * 60)

    client = get_secrets_client(use_localstack=True)
    secret_name = "example/rotating-secret"

    # Clean up from previous runs
    try:
        client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
        time.sleep(1)
    except Exception:
        pass

    # 1. Create initial secret
    print("\n1. Creating initial database secret...")
    initial_secret = {
        "host": "db.example.com",
        "port": 5432,
        "database": "myapp",
        "username": "app_user",
        "password": generate_password(24),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    client.create_secret(
        Name=secret_name,
        SecretString=json.dumps(initial_secret),
        Description="Database credentials with rotation",
    )
    print(f"   Created: {secret_name}")
    print(f"   Initial password: {initial_secret['password'][:8]}...")

    # 2. Show current state
    print("\n2. Current secret state:")
    metadata = client.describe_secret(SecretId=secret_name)
    for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
        print(f"   Version: {version_id[:8]}... Stages: {stages}")

    # 3. Perform rotation
    print("\n3. Performing rotation...")
    handler = DatabaseRotationHandler(client)
    handler.rotate(secret_name)

    # 4. Show post-rotation state
    print("\n4. Post-rotation secret state:")
    metadata = client.describe_secret(SecretId=secret_name)
    for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
        print(f"   Version: {version_id[:8]}... Stages: {stages}")

    # 5. Verify new secret
    print("\n5. Verifying rotated secret:")
    current = client.get_secret_value(
        SecretId=secret_name,
        VersionStage="AWSCURRENT",
    )
    current_secret = json.loads(current["SecretString"])
    print(f"   New password: {current_secret['password'][:8]}...")
    print(f"   Rotated at: {current_secret.get('rotated_at', 'N/A')}")

    # 6. Perform another rotation
    print("\n6. Performing second rotation...")
    handler.rotate(secret_name)

    # 7. Show final state with AWSPREVIOUS
    print("\n7. Final secret state (showing history):")
    metadata = client.describe_secret(SecretId=secret_name)
    for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
        print(f"   Version: {version_id[:8]}... Stages: {stages}")

    # Clean up
    print("\n8. Cleaning up...")
    client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
    print(f"   Deleted: {secret_name}")

    print("\n" + "=" * 60)
    print("Example 3 Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Rotation uses 4 steps: create, set, test, finish")
    print("- AWSPENDING holds new credentials during rotation")
    print("- AWSPREVIOUS allows rollback if issues arise")
    print("- In production, AWS Lambda executes these steps")


if __name__ == "__main__":
    main()

"""Solution 3: API Key Rotation Handler.

This solution demonstrates a complete API key rotation handler
following the AWS Secrets Manager rotation protocol.
"""

from __future__ import annotations

import json
import secrets
import string
import time
import uuid
from typing import Any

from botocore.exceptions import ClientError


def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate a secure API key.

    Args:
        prefix: Key prefix (e.g., "sk" for secret key)
        length: Length of the random portion

    Returns:
        API key in format: prefix_randomstring
    """
    # Use URL-safe characters for API keys
    alphabet = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{random_part}"


class ExternalAPIClient:
    """Simulated external API client for testing.

    This simulates an external service where we need to rotate API keys.
    In production, this would make real HTTP requests.
    """

    def __init__(self):
        self._current_key: str | None = None
        self._pending_key: str | None = None

    def create_api_key(self, key: str) -> None:
        """Register a new API key (pending activation).

        Args:
            key: The new API key to register
        """
        self._pending_key = key

    def activate_api_key(self, key: str) -> None:
        """Activate a pending API key.

        Args:
            key: The key to activate

        Raises:
            ValueError: If key doesn't match pending key
        """
        if key != self._pending_key:
            raise ValueError("Key doesn't match pending key")
        self._current_key = key
        self._pending_key = None

    def test_api_key(self, key: str) -> bool:
        """Test if an API key is valid.

        Args:
            key: The key to test

        Returns:
            True if key is valid (current or pending)
        """
        return key in (self._current_key, self._pending_key)

    def revoke_api_key(self, key: str) -> None:
        """Revoke an API key.

        Args:
            key: The key to revoke
        """
        if key == self._current_key:
            self._current_key = None
        if key == self._pending_key:
            self._pending_key = None


class APIKeyRotationHandler:
    """Rotation handler for API keys.

    Implements the AWS Secrets Manager rotation protocol:
    1. createSecret - Generate new API key, store as AWSPENDING
    2. setSecret - Register new key with external service
    3. testSecret - Verify new key works
    4. finishSecret - Activate key and update version stages
    """

    def __init__(self, secrets_client: Any, api_client: ExternalAPIClient):
        """Initialize the handler.

        Args:
            secrets_client: boto3 secretsmanager client
            api_client: External API client for key management
        """
        self.secrets_client = secrets_client
        self.api_client = api_client

    def rotate(self, secret_id: str) -> None:
        """Perform a complete rotation.

        Args:
            secret_id: The secret to rotate
        """
        # Generate a unique token for this rotation
        token = str(uuid.uuid4())

        print(f"\n   Starting rotation for: {secret_id}")
        print(f"   Rotation token: {token[:8]}...")

        # Execute rotation steps in order
        self._create_secret(secret_id, token)
        self._set_secret(secret_id, token)
        self._test_secret(secret_id, token)
        self._finish_secret(secret_id, token)

        print("   Rotation complete!")

    def _create_secret(self, secret_id: str, token: str) -> None:
        """Step 1: Create new API key version with AWSPENDING stage.

        Args:
            secret_id: The secret to rotate
            token: Unique rotation token
        """
        print("\n   Step 1: createSecret")

        # Check for idempotency - see if AWSPENDING already exists
        try:
            self.secrets_client.get_secret_value(
                SecretId=secret_id,
                VersionId=token,
                VersionStage="AWSPENDING",
            )
            print("      AWSPENDING already exists, skipping")
            return
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                raise

        # Get current secret
        current_response = self.secrets_client.get_secret_value(
            SecretId=secret_id,
            VersionStage="AWSCURRENT",
        )
        current_secret = json.loads(current_response["SecretString"])
        print(f"      Current key: {current_secret['api_key'][:12]}...")

        # Generate new API key
        new_api_key = generate_api_key()
        new_secret = {
            **current_secret,
            "api_key": new_api_key,
            "rotated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "previous_key": current_secret["api_key"],
        }
        print(f"      New key: {new_api_key[:12]}...")

        # Store as AWSPENDING
        self.secrets_client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps(new_secret),
            VersionStages=["AWSPENDING"],
        )
        print("      Stored new version as AWSPENDING")

    def _set_secret(self, secret_id: str, token: str) -> None:
        """Step 2: Register new key with external service.

        Args:
            secret_id: The secret being rotated
            token: Rotation token
        """
        print("\n   Step 2: setSecret")

        # Get pending secret
        pending_response = self.secrets_client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage="AWSPENDING",
        )
        secret = json.loads(pending_response["SecretString"])

        # Register with external service
        self.api_client.create_api_key(secret["api_key"])
        print(f"      Registered key with external service")

    def _test_secret(self, secret_id: str, token: str) -> None:
        """Step 3: Test new key works.

        Args:
            secret_id: The secret being rotated
            token: Rotation token

        Raises:
            RuntimeError: If key test fails
        """
        print("\n   Step 3: testSecret")

        # Get pending secret
        pending_response = self.secrets_client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage="AWSPENDING",
        )
        secret = json.loads(pending_response["SecretString"])

        # Test the key
        if not self.api_client.test_api_key(secret["api_key"]):
            raise RuntimeError(
                f"API key test failed for secret {secret_id}. "
                "The new key is not recognized by the external service."
            )

        print("      Key test passed")

    def _finish_secret(self, secret_id: str, token: str) -> None:
        """Step 4: Finalize rotation.

        Args:
            secret_id: The secret being rotated
            token: Rotation token
        """
        print("\n   Step 4: finishSecret")

        # Get pending secret to activate the key
        pending_response = self.secrets_client.get_secret_value(
            SecretId=secret_id,
            VersionId=token,
            VersionStage="AWSPENDING",
        )
        secret = json.loads(pending_response["SecretString"])

        # Activate the key with external service
        self.api_client.activate_api_key(secret["api_key"])
        print("      Activated key with external service")

        # Get metadata to find current version
        metadata = self.secrets_client.describe_secret(SecretId=secret_id)

        current_version = None
        for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
            if "AWSCURRENT" in stages:
                if version_id == token:
                    print("      Already current, skipping stage update")
                    return
                current_version = version_id
                break

        # Move AWSCURRENT to the new version
        self.secrets_client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage="AWSCURRENT",
            MoveToVersionId=token,
            RemoveFromVersionId=current_version,
        )
        print(f"      Moved AWSCURRENT to new version")

        # Optionally revoke the old key after a grace period
        # In production, you might want to keep it active briefly
        # self.api_client.revoke_api_key(secret.get("previous_key"))


def main() -> None:
    """Demonstrate the APIKeyRotationHandler."""
    import os

    from secrets_manager import get_secrets_client

    os.environ.setdefault("USE_LOCALSTACK", "1")

    print("=" * 60)
    print("Solution 3: API Key Rotation Handler")
    print("=" * 60)

    secrets_client = get_secrets_client(use_localstack=True)
    api_client = ExternalAPIClient()

    secret_name = "test/api-key"

    # Clean up previous runs
    try:
        secrets_client.delete_secret(
            SecretId=secret_name, ForceDeleteWithoutRecovery=True
        )
        time.sleep(1)
    except Exception:
        pass

    # Create initial secret
    print("\n1. Creating initial API key...")
    initial_key = generate_api_key()
    secrets_client.create_secret(
        Name=secret_name,
        SecretString=json.dumps({
            "api_key": initial_key,
            "service": "external-api",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }),
    )

    # Simulate the key being active in the external service
    api_client._current_key = initial_key

    print(f"   Initial key: {initial_key}")
    print(f"   External service has key: {api_client.test_api_key(initial_key)}")

    # Show initial state
    print("\n2. Initial secret state:")
    metadata = secrets_client.describe_secret(SecretId=secret_name)
    for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
        print(f"   Version: {version_id[:8]}... Stages: {stages}")

    # Perform rotation
    print("\n3. Performing rotation...")
    handler = APIKeyRotationHandler(secrets_client, api_client)
    handler.rotate(secret_name)

    # Show post-rotation state
    print("\n4. Post-rotation state:")
    metadata = secrets_client.describe_secret(SecretId=secret_name)
    for version_id, stages in metadata.get("VersionIdsToStages", {}).items():
        print(f"   Version: {version_id[:8]}... Stages: {stages}")

    # Verify new key
    print("\n5. Verifying rotation:")
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])
    new_key = secret["api_key"]
    print(f"   New key: {new_key}")
    print(f"   Previous key stored: {secret.get('previous_key', 'N/A')}")
    print(f"   Rotated at: {secret.get('rotated_at', 'N/A')}")
    print(f"   External service accepts new key: {api_client.test_api_key(new_key)}")
    print(f"   External service rejects old key: {not api_client.test_api_key(initial_key)}")

    # Perform another rotation
    print("\n6. Performing second rotation...")
    handler.rotate(secret_name)

    # Final state
    print("\n7. Final state:")
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])
    print(f"   Current key: {secret['api_key']}")
    print(f"   Previous key: {secret.get('previous_key', 'N/A')[:20]}...")

    # Clean up
    print("\n8. Cleaning up...")
    secrets_client.delete_secret(
        SecretId=secret_name, ForceDeleteWithoutRecovery=True
    )

    print("\n" + "=" * 60)
    print("Solution 3 Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Always check for idempotency in createSecret")
    print("- Test the new credentials before finalizing")
    print("- Store the previous key for potential rollback")
    print("- Activate with external service before updating stages")


if __name__ == "__main__":
    main()

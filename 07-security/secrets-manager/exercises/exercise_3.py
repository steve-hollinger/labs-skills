"""Exercise 3: API Key Rotation Handler.

Create a rotation handler for API keys that:
1. Generates new API keys using a secure method
2. Updates the external service (simulated)
3. Tests the new key works
4. Handles rollback on failure

Expected usage:
    handler = APIKeyRotationHandler(client, api_client)
    handler.rotate("myapp/api-key")

Hints:
- Extend the base RotationHandler pattern
- Use secrets module for key generation
- Implement proper error handling for each step
- Consider idempotency (rotation might be retried)
"""

from __future__ import annotations

import secrets
import string
from abc import ABC, abstractmethod
from typing import Any


def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate a secure API key.

    Args:
        prefix: Key prefix (e.g., "sk" for secret key)
        length: Length of the random portion

    Returns:
        API key in format: prefix_randomstring
    """
    # TODO: Implement secure key generation
    # Hint: Use secrets.choice with alphanumeric characters
    raise NotImplementedError("Implement generate_api_key")


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

    TODO: Implement the rotation protocol:
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
        # TODO: Store clients
        pass

    def rotate(self, secret_id: str) -> None:
        """Perform a complete rotation.

        Args:
            secret_id: The secret to rotate

        This should:
        1. Generate a rotation token
        2. Execute all 4 rotation steps
        3. Handle errors appropriately
        """
        # TODO: Implement rotation orchestration
        raise NotImplementedError("Implement rotate")

    def _create_secret(self, secret_id: str, token: str) -> None:
        """Step 1: Create new API key version.

        Args:
            secret_id: The secret to rotate
            token: Unique rotation token
        """
        # TODO: Implement createSecret step
        # 1. Check if AWSPENDING already exists (idempotency)
        # 2. Get current secret
        # 3. Generate new API key
        # 4. Store as AWSPENDING
        raise NotImplementedError("Implement _create_secret")

    def _set_secret(self, secret_id: str, token: str) -> None:
        """Step 2: Register new key with external service.

        Args:
            secret_id: The secret being rotated
            token: Rotation token
        """
        # TODO: Implement setSecret step
        # 1. Get AWSPENDING secret
        # 2. Register key with external service
        raise NotImplementedError("Implement _set_secret")

    def _test_secret(self, secret_id: str, token: str) -> None:
        """Step 3: Test new key works.

        Args:
            secret_id: The secret being rotated
            token: Rotation token

        Raises:
            RuntimeError: If key test fails
        """
        # TODO: Implement testSecret step
        # 1. Get AWSPENDING secret
        # 2. Test key with external service
        # 3. Raise error if test fails
        raise NotImplementedError("Implement _test_secret")

    def _finish_secret(self, secret_id: str, token: str) -> None:
        """Step 4: Finalize rotation.

        Args:
            secret_id: The secret being rotated
            token: Rotation token
        """
        # TODO: Implement finishSecret step
        # 1. Activate key with external service
        # 2. Move AWSCURRENT stage to new version
        # 3. Old version becomes AWSPREVIOUS
        raise NotImplementedError("Implement _finish_secret")


def main() -> None:
    """Test your implementation."""
    print("Exercise 3: Implement APIKeyRotationHandler")
    print("See the solution in solutions/solution_3.py")

    # Uncomment to test your implementation:
    #
    # from secrets_manager import get_secrets_client
    # import os
    # import json
    # os.environ.setdefault("USE_LOCALSTACK", "1")
    #
    # secrets_client = get_secrets_client(use_localstack=True)
    # api_client = ExternalAPIClient()
    #
    # # Create initial secret
    # secret_name = "test/api-key"
    # try:
    #     secrets_client.delete_secret(
    #         SecretId=secret_name,
    #         ForceDeleteWithoutRecovery=True
    #     )
    # except Exception:
    #     pass
    #
    # initial_key = generate_api_key()
    # secrets_client.create_secret(
    #     Name=secret_name,
    #     SecretString=json.dumps({
    #         "api_key": initial_key,
    #         "created_at": "2024-01-01T00:00:00Z"
    #     })
    # )
    # api_client.activate_api_key(initial_key)
    #
    # print(f"Initial key: {initial_key[:12]}...")
    #
    # # Rotate
    # handler = APIKeyRotationHandler(secrets_client, api_client)
    # handler.rotate(secret_name)
    #
    # # Verify
    # response = secrets_client.get_secret_value(SecretId=secret_name)
    # new_secret = json.loads(response["SecretString"])
    # print(f"New key: {new_secret['api_key'][:12]}...")


if __name__ == "__main__":
    main()

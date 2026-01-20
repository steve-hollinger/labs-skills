"""Example 1: Basic API Key Generation and Validation.

This example demonstrates:
- Generating secure API keys
- Storing keys with hashing
- Validating keys against a store

Run with: make example-1
"""

from __future__ import annotations

from datetime import datetime, timedelta

from api_key_auth import (
    APIKeyInfo,
    APIKeyValidator,
    KeyStore,
    ValidationResult,
    generate_api_key,
    get_key_prefix,
    hash_key,
    validate_key_format,
)
from api_key_auth.generator import (
    generate_key_pair,
    mask_key,
    parse_key_parts,
)
from api_key_auth.storage import KeyStatus, KeyTier


def main() -> None:
    """Demonstrate basic API key operations."""
    print("=" * 60)
    print("Example 1: Basic API Key Generation and Validation")
    print("=" * 60)

    # 1. Generate API keys
    print("\n1. Generating API Keys")
    print("-" * 40)

    # Simple key
    simple_key = generate_api_key("sk")
    print(f"Simple key: {simple_key}")

    # Key with environment prefix
    live_key = generate_api_key("sk_live")
    test_key = generate_api_key("sk_test")
    print(f"Live key: {live_key}")
    print(f"Test key: {test_key}")

    # Key pair (public/secret)
    public_key, secret_key = generate_key_pair(environment="live")
    print(f"\nKey pair:")
    print(f"  Public:  {public_key}")
    print(f"  Secret:  {secret_key}")

    # 2. Key format and masking
    print("\n2. Key Format and Masking")
    print("-" * 40)

    print(f"Full key:    {live_key}")
    print(f"Prefix:      {get_key_prefix(live_key)}")
    print(f"Masked:      {mask_key(live_key)}")

    parts = parse_key_parts(live_key)
    print(f"Parsed parts: {parts}")

    # 3. Key validation (format only)
    print("\n3. Format Validation")
    print("-" * 40)

    test_keys = [
        ("sk_example_FAKE", "sk_live"),
        ("pk_test_abc123", "pk"),
        ("invalid", None),
        ("sk_abc", "sk"),  # Too short
    ]

    for key, prefix in test_keys:
        valid, error = validate_key_format(key, prefix, min_length=15)
        status = "Valid" if valid else f"Invalid: {error}"
        print(f"  {key[:20]:20} -> {status}")

    # 4. Storing keys (with hashing)
    print("\n4. Storing Keys")
    print("-" * 40)

    store = KeyStore()

    # Store some keys
    user_key = generate_api_key("sk_live")
    admin_key = generate_api_key("sk_live")

    user_info = store.store(
        key=user_key,
        name="User API Key",
        owner_id="user_123",
        tier=KeyTier.BASIC,
    )
    print(f"Stored user key: {user_info.key_prefix}")
    print(f"  ID: {user_info.id}")
    print(f"  Hash: {user_info.key_hash[:16]}...")

    admin_info = store.store(
        key=admin_key,
        name="Admin API Key",
        owner_id="admin_456",
        tier=KeyTier.PRO,
        metadata={"scopes": ["read", "write", "admin"]},
    )
    print(f"\nStored admin key: {admin_info.key_prefix}")
    print(f"  Tier: {admin_info.tier.value}")
    print(f"  Scopes: {admin_info.metadata.get('scopes')}")

    # 5. Validating keys
    print("\n5. Validating Keys")
    print("-" * 40)

    validator = APIKeyValidator(store)

    # Valid key
    response = validator.validate(user_key)
    print(f"User key validation: {response.result.value}")
    print(f"  Key name: {response.key_info.name if response.key_info else 'N/A'}")

    # Invalid key
    response = validator.validate("sk_example_FAKE")
    print(f"\nInvalid key validation: {response.result.value}")
    print(f"  Message: {response.message}")

    # No key provided
    response = validator.validate(None)
    print(f"\nNo key validation: {response.result.value}")
    print(f"  Message: {response.message}")

    # 6. Key revocation
    print("\n6. Key Revocation")
    print("-" * 40)

    print(f"User key status before: {user_info.status.value}")

    store.revoke(user_info.id, reason="Security concern")

    print(f"User key status after: {user_info.status.value}")

    response = validator.validate(user_key)
    print(f"Validation result: {response.result.value}")
    print(f"  Message: {response.message}")

    # 7. Key expiration
    print("\n7. Key Expiration")
    print("-" * 40)

    expiring_key = generate_api_key("sk_live")
    expires_at = datetime.utcnow() - timedelta(hours=1)  # Already expired

    expired_info = store.store(
        key=expiring_key,
        name="Expired Key",
        owner_id="user_789",
        expires_at=expires_at,
    )

    print(f"Key expires at: {expires_at}")
    print(f"Is expired: {expired_info.is_expired}")

    response = validator.validate(expiring_key)
    print(f"Validation result: {response.result.value}")

    # 8. Listing keys
    print("\n8. Listing Keys")
    print("-" * 40)

    all_keys = store.list_keys()
    print(f"Total keys: {len(all_keys)}")

    active_keys = store.list_keys(status=KeyStatus.ACTIVE)
    print(f"Active keys: {len(active_keys)}")

    pro_keys = store.list_keys(tier=KeyTier.PRO)
    print(f"Pro tier keys: {len(pro_keys)}")

    print("\n" + "=" * 60)
    print("Example 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

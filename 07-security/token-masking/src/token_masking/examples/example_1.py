"""Example 1: Basic Token Masking.

This example demonstrates fundamental masking operations:
- Full masking (complete replacement)
- Partial masking (show prefix/suffix)
- Email masking (preserve format)
- URL credential masking

Run with: make example-1
"""

from __future__ import annotations

from token_masking import (
    TokenMasker,
    full_mask,
    mask_email,
    mask_json,
    mask_url_credentials,
    partial_mask,
)


def main() -> None:
    """Demonstrate basic masking operations."""
    print("=" * 60)
    print("Example 1: Basic Token Masking")
    print("=" * 60)

    # 1. Full masking
    print("\n1. Full Masking")
    print("-" * 40)

    password = "super-secret-password-123"
    print(f"Original: {password}")
    print(f"Masked:   {full_mask(password)}")

    # With custom placeholder
    print(f"Custom:   {full_mask(password, placeholder='[REDACTED]')}")

    # 2. Partial masking
    print("\n2. Partial Masking")
    print("-" * 40)

    api_key = "sk_example_FAKE"
    print(f"Original: {api_key}")
    print(f"Default:  {partial_mask(api_key)}")
    print(f"More:     {partial_mask(api_key, show_start=7, show_end=4)}")
    print(f"Less:     {partial_mask(api_key, show_start=2, show_end=2)}")

    # Short value handling
    short_secret = "abc"
    print(f"\nShort secret: '{short_secret}'")
    print(f"Masked:       '{partial_mask(short_secret)}'")

    # 3. Email masking
    print("\n3. Email Masking")
    print("-" * 40)

    emails = [
        "john.doe@example.com",
        "a@b.com",
        "user.name+tag@subdomain.example.org",
    ]

    for email in emails:
        print(f"Original: {email}")
        print(f"Masked:   {mask_email(email)}")
        print()

    # 4. URL credential masking
    print("4. URL Credential Masking")
    print("-" * 40)

    urls = [
        "postgres://admin:super-secret@db.example.com:5432/myapp",
        "redis://default:p@ssw0rd@cache.example.com:6379",
        "https://api:token123@api.service.com/v1/data",
        "https://api.service.com/v1/data",  # No credentials
    ]

    for url in urls:
        print(f"Original: {url}")
        print(f"Masked:   {mask_url_credentials(url)}")
        print()

    # 5. JSON field masking
    print("5. JSON Field Masking")
    print("-" * 40)

    config = {
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "username": "app_user",
            "password": "db-password-123",
        },
        "api": {
            "endpoint": "https://api.example.com",
            "api_key": "sk_example_FAKE",
            "timeout": 30,
        },
        "logging": {
            "level": "INFO",
            "token": "logging-token-456",
        },
    }

    import json
    print("Original:")
    print(json.dumps(config, indent=2))

    masked_config = mask_json(config)
    print("\nMasked:")
    print(json.dumps(masked_config, indent=2))

    # 6. Using TokenMasker class
    print("\n6. Using TokenMasker Class")
    print("-" * 40)

    masker = TokenMasker()

    # Text with mixed secrets
    text = """
    Connecting to database at postgres://admin:secret123@db.example.com
    Using API key: sk_example_FAKE
    Contact: support@example.com
    GitHub token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    AWS Key: AKIAIOSFODNN7EXAMPLE
    """

    print("Original text:")
    print(text)

    print("\nMasked text:")
    print(masker.mask_text(text))

    # Detect secrets
    print("\nDetected secrets:")
    secrets = masker.detect_secrets(text)
    for secret in secrets:
        print(f"  - Type: {secret['type']}, Masked: {secret['masked']}")

    print("\n" + "=" * 60)
    print("Example 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

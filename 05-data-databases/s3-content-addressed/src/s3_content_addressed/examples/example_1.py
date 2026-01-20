"""Example 1: Basic Content-Addressed Store

This example demonstrates the fundamental operations of a content-addressed
store: storing, retrieving, and verifying content using hash-based keys.

Key concepts:
- Computing content hashes
- Storing content with hash as key
- Automatic deduplication
- Integrity verification on retrieval
"""

import boto3
from moto import mock_aws

from s3_content_addressed.hasher import compute_hash, short_hash
from s3_content_addressed.store import ContentAddressedStore, IntegrityError


def demonstrate_basic_operations(store: ContentAddressedStore) -> None:
    """Demonstrate basic CAS operations.

    Args:
        store: Content-addressed store instance
    """
    print("\n--- Basic Store Operations ---\n")

    # Store some content
    content1 = b"Hello, Content-Addressed World!"
    result1 = store.store(content1)

    print(f"Stored: 'Hello, Content-Addressed World!'")
    print(f"  Hash: {short_hash(result1.content_hash)}...")
    print(f"  Size: {result1.size_bytes} bytes")
    print(f"  Deduplicated: {result1.was_deduplicated}")

    # Store same content again - should be deduplicated
    result2 = store.store(content1)

    print(f"\nStored same content again:")
    print(f"  Hash: {short_hash(result2.content_hash)}... (same!)")
    print(f"  Deduplicated: {result2.was_deduplicated}")

    # Store different content
    content2 = b"Different content here"
    result3 = store.store(content2)

    print(f"\nStored: 'Different content here'")
    print(f"  Hash: {short_hash(result3.content_hash)}... (different)")
    print(f"  Deduplicated: {result3.was_deduplicated}")


def demonstrate_retrieval_and_verification(store: ContentAddressedStore) -> None:
    """Demonstrate content retrieval with verification.

    Args:
        store: Content-addressed store instance
    """
    print("\n--- Retrieval and Verification ---\n")

    # Store content
    original = b"Important data that must not be corrupted"
    result = store.store(original)
    content_hash = result.content_hash

    print(f"Stored: 'Important data that must not be corrupted'")
    print(f"  Hash: {short_hash(content_hash)}...")

    # Retrieve with verification
    retrieved = store.get(content_hash, verify=True)
    print(f"\nRetrieved (with verification): '{retrieved.decode()}'")

    # Verify integrity separately
    is_valid = store.verify_integrity(content_hash)
    print(f"Integrity check passed: {is_valid}")

    # Demonstrate what happens with invalid hash
    print("\n--- Integrity Error Demonstration ---")
    print("Attempting to retrieve with wrong hash...")

    # This would raise an error in production
    # (We can't simulate corruption in S3, but the verification logic works)
    fake_hash = "0" * 64
    try:
        store.get(fake_hash)
    except Exception as e:
        print(f"  Error (expected): {type(e).__name__}")


def demonstrate_deduplication_savings(store: ContentAddressedStore) -> None:
    """Demonstrate storage savings from deduplication.

    Args:
        store: Content-addressed store instance
    """
    print("\n--- Deduplication Savings ---\n")

    # Simulate storing the same file multiple times
    # (like multiple users uploading the same attachment)
    shared_file = b"This is a shared document that many users upload." * 100

    uploads = []
    for i in range(5):
        result = store.store(shared_file)
        uploads.append(result)
        dedup_status = "DEDUP" if result.was_deduplicated else "NEW"
        print(f"Upload {i+1}: {dedup_status} - {short_hash(result.content_hash)}...")

    # Calculate savings
    total_uploaded = len(shared_file) * 5
    actual_stored = len(shared_file)  # Only one copy
    savings = total_uploaded - actual_stored
    savings_percent = (savings / total_uploaded) * 100

    print(f"\nStorage Analysis:")
    print(f"  Total data uploaded: {total_uploaded:,} bytes")
    print(f"  Actual data stored: {actual_stored:,} bytes")
    print(f"  Savings: {savings:,} bytes ({savings_percent:.1f}%)")


def demonstrate_existence_check(store: ContentAddressedStore) -> None:
    """Demonstrate checking if content exists.

    Args:
        store: Content-addressed store instance
    """
    print("\n--- Existence Checks ---\n")

    # Store some content
    content = b"Content to check"
    result = store.store(content)
    existing_hash = result.content_hash

    # Check existing
    exists = store.exists(existing_hash)
    print(f"Hash {short_hash(existing_hash)}... exists: {exists}")

    # Check non-existing
    fake_hash = "a" * 64
    exists = store.exists(fake_hash)
    print(f"Hash {short_hash(fake_hash)}... exists: {exists}")

    # Pre-check before upload (optimization)
    new_content = b"Potentially new content"
    new_hash = compute_hash(new_content)

    if store.exists(new_hash):
        print(f"\nContent already exists, skipping upload")
    else:
        print(f"\nContent is new, uploading...")
        store.store(new_content)


@mock_aws
def main() -> None:
    """Run the basic content-addressed store example."""
    print("Example 1: Basic Content-Addressed Store")
    print("=" * 50)

    # Set up S3
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "content-addressed-demo"
    s3.create_bucket(Bucket=bucket_name)

    # Create content-addressed store
    store = ContentAddressedStore(s3, bucket_name)

    # Run demonstrations
    demonstrate_basic_operations(store)
    demonstrate_retrieval_and_verification(store)
    demonstrate_deduplication_savings(store)
    demonstrate_existence_check(store)

    # Final summary
    print("\n" + "=" * 50)
    print("Key Takeaways:")
    print("1. Content is addressed by its hash, not a user-chosen name")
    print("2. Same content always produces same hash -> automatic dedup")
    print("3. Verification ensures content hasn't changed or been corrupted")
    print("4. Check existence before upload to save bandwidth")
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()

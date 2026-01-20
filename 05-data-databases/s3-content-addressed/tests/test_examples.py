"""Tests for S3 Content-Addressed Storage examples."""

import boto3
import pytest
from moto import mock_aws

from s3_content_addressed.hasher import (
    compute_hash,
    compute_hash_streaming,
    short_hash,
    verify_hash,
)
from s3_content_addressed.store import (
    ChunkedStore,
    ContentAddressedStore,
    IntegrityError,
)


class TestHasher:
    """Tests for hashing utilities."""

    def test_compute_hash_deterministic(self) -> None:
        """Test that same content produces same hash."""
        data = b"Hello, World!"
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        assert hash1 == hash2

    def test_compute_hash_different_content(self) -> None:
        """Test that different content produces different hash."""
        hash1 = compute_hash(b"Content A")
        hash2 = compute_hash(b"Content B")
        assert hash1 != hash2

    def test_compute_hash_sha256_length(self) -> None:
        """Test SHA-256 produces 64-character hex string."""
        hash_val = compute_hash(b"test")
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_compute_hash_streaming(self) -> None:
        """Test streaming hash matches regular hash."""
        import io
        data = b"Test data for streaming hash"

        regular_hash = compute_hash(data)
        streaming_hash = compute_hash_streaming(io.BytesIO(data))

        assert regular_hash == streaming_hash

    def test_verify_hash_valid(self) -> None:
        """Test verify_hash returns True for matching content."""
        data = b"Verify me"
        hash_val = compute_hash(data)
        assert verify_hash(data, hash_val) is True

    def test_verify_hash_invalid(self) -> None:
        """Test verify_hash returns False for mismatched content."""
        data = b"Original"
        hash_val = compute_hash(data)
        assert verify_hash(b"Modified", hash_val) is False

    def test_short_hash(self) -> None:
        """Test short_hash truncates correctly."""
        full_hash = "abcdef0123456789" * 4
        assert short_hash(full_hash) == "abcdef01"
        assert short_hash(full_hash, 4) == "abcd"


@mock_aws
class TestContentAddressedStore:
    """Tests for ContentAddressedStore."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.s3 = boto3.client("s3", region_name="us-east-1")
        self.bucket = "test-bucket"
        self.s3.create_bucket(Bucket=self.bucket)
        self.store = ContentAddressedStore(self.s3, self.bucket)

    def test_store_and_retrieve(self) -> None:
        """Test basic store and retrieve."""
        data = b"Test content"
        result = self.store.store(data)

        retrieved = self.store.get(result.content_hash)
        assert retrieved == data

    def test_store_returns_hash(self) -> None:
        """Test that store returns correct hash."""
        data = b"Content to hash"
        expected_hash = compute_hash(data)

        result = self.store.store(data)
        assert result.content_hash == expected_hash

    def test_deduplication(self) -> None:
        """Test that duplicate content is deduplicated."""
        data = b"Duplicate me"

        result1 = self.store.store(data)
        result2 = self.store.store(data)

        assert result1.content_hash == result2.content_hash
        assert result1.was_deduplicated is False
        assert result2.was_deduplicated is True

    def test_exists(self) -> None:
        """Test exists check."""
        data = b"Check existence"
        result = self.store.store(data)

        assert self.store.exists(result.content_hash) is True
        assert self.store.exists("nonexistent" + "0" * 56) is False

    def test_delete(self) -> None:
        """Test content deletion."""
        data = b"Delete me"
        result = self.store.store(data)

        assert self.store.exists(result.content_hash) is True

        deleted = self.store.delete(result.content_hash)
        assert deleted is True
        assert self.store.exists(result.content_hash) is False

    def test_delete_nonexistent(self) -> None:
        """Test deleting non-existent content."""
        deleted = self.store.delete("0" * 64)
        assert deleted is False

    def test_get_verified(self) -> None:
        """Test retrieval with verification."""
        data = b"Verify on retrieve"
        result = self.store.store(data)

        # Should succeed with verification
        retrieved = self.store.get(result.content_hash, verify=True)
        assert retrieved == data

    def test_verify_integrity(self) -> None:
        """Test integrity verification."""
        data = b"Check my integrity"
        result = self.store.store(data)

        assert self.store.verify_integrity(result.content_hash) is True

    def test_list_objects(self) -> None:
        """Test listing stored objects."""
        data1 = b"Object 1"
        data2 = b"Object 2"

        result1 = self.store.store(data1)
        result2 = self.store.store(data2)

        hashes = self.store.list_objects()
        assert result1.content_hash in hashes
        assert result2.content_hash in hashes

    def test_list_objects_with_limit(self) -> None:
        """Test listing with limit."""
        for i in range(5):
            self.store.store(f"Object {i}".encode())

        hashes = self.store.list_objects(limit=3)
        assert len(hashes) == 3

    def test_get_metadata(self) -> None:
        """Test getting object metadata."""
        data = b"Get my metadata"
        result = self.store.store(data)

        metadata = self.store.get_metadata(result.content_hash)
        assert metadata["content_hash"] == result.content_hash
        assert metadata["size_bytes"] == len(data)


@mock_aws
class TestChunkedStore:
    """Tests for ChunkedStore."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.s3 = boto3.client("s3", region_name="us-east-1")
        self.bucket = "test-chunked"
        self.s3.create_bucket(Bucket=self.bucket)
        self.store = ChunkedStore(self.s3, self.bucket, chunk_size=100)

    def test_store_and_retrieve_chunked(self) -> None:
        """Test chunked store and retrieve."""
        # Create data larger than chunk size
        data = b"A" * 250  # Will be split into 3 chunks

        result = self.store.store_chunked(data)
        assert result["chunk_count"] == 3

        retrieved = self.store.retrieve_chunked(result["manifest_hash"])
        assert retrieved == data

    def test_chunk_deduplication(self) -> None:
        """Test deduplication across chunks."""
        # Create data with repeated chunks
        chunk = b"X" * 100
        data = chunk + chunk + chunk  # Same chunk 3 times

        result = self.store.store_chunked(data)

        # Should have 3 chunks but only 1 unique (deduped)
        assert result["chunk_count"] == 3
        assert result["new_chunks"] == 1  # Only one unique chunk
        assert result["deduped_chunks"] == 2

    def test_small_file_single_chunk(self) -> None:
        """Test small file fits in single chunk."""
        data = b"Small"  # Less than chunk size

        result = self.store.store_chunked(data)
        assert result["chunk_count"] == 1

        retrieved = self.store.retrieve_chunked(result["manifest_hash"])
        assert retrieved == data


@mock_aws
class TestCopyBetweenStores:
    """Tests for copying between stores."""

    def test_copy_to_another_store(self) -> None:
        """Test copying content between stores."""
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="source")
        s3.create_bucket(Bucket="dest")

        source = ContentAddressedStore(s3, "source")
        dest = ContentAddressedStore(s3, "dest")

        # Store in source
        data = b"Copy me"
        result = source.store(data)

        # Copy to dest
        copied = source.copy_to(result.content_hash, dest)
        assert copied is True

        # Verify in dest
        assert dest.exists(result.content_hash)
        retrieved = dest.get(result.content_hash)
        assert retrieved == data

    def test_copy_existing_skipped(self) -> None:
        """Test that copy skips if already exists in dest."""
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="source")
        s3.create_bucket(Bucket="dest")

        source = ContentAddressedStore(s3, "source")
        dest = ContentAddressedStore(s3, "dest")

        data = b"Already there"
        result = source.store(data)
        dest.store(data)  # Already in dest

        # Copy should return False (already exists)
        copied = source.copy_to(result.content_hash, dest)
        assert copied is False

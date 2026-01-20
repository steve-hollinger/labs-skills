# Core Concepts

## Overview

Content-addressed storage (CAS) is a storage paradigm where data is identified by its content rather than a user-assigned name or location. The "address" of data is derived from its cryptographic hash, providing unique properties ideal for deduplication, integrity verification, and immutable data systems.

## Concept 1: Content Hashing

### What It Is

Content hashing is the process of computing a fixed-size fingerprint (hash) from variable-size data. The hash serves as both the identifier and integrity check for the content.

### Why It Matters

- **Unique identification**: Same content always produces same hash
- **Integrity verification**: Any change produces different hash
- **Efficient comparison**: Compare hashes instead of entire content
- **Deterministic**: No coordination needed for naming

### How It Works

```python
import hashlib
from typing import BinaryIO


def compute_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Compute content hash using specified algorithm.

    Args:
        data: Content to hash
        algorithm: Hash algorithm (sha256, sha1, md5)

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def compute_hash_streaming(stream: BinaryIO, chunk_size: int = 8192) -> str:
    """Compute hash of large file without loading into memory.

    Args:
        stream: File-like object to hash
        chunk_size: Size of chunks to read

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.sha256()
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()


# Examples
text = b"Hello, World!"
hash1 = compute_hash(text)  # Same text -> same hash
hash2 = compute_hash(text)  # hash1 == hash2

modified = b"Hello, World!!"
hash3 = compute_hash(modified)  # Different! (one extra char)
```

## Concept 2: Deduplication

### What It Is

Deduplication (dedup) is the elimination of duplicate data by storing only unique content. CAS naturally enables dedup since identical content produces identical addresses.

### Why It Matters

- **Storage savings**: Store identical content only once
- **Bandwidth reduction**: Don't transfer what's already stored
- **Cost efficiency**: Pay for unique data only
- **Environmental**: Less storage = less energy

### How It Works

```python
class ContentStore:
    """Content-addressed store with automatic deduplication."""

    def __init__(self, s3_client, bucket: str):
        self.s3 = s3_client
        self.bucket = bucket

    def store(self, data: bytes) -> str:
        """Store content, returning its hash. Deduplicates automatically."""
        content_hash = hashlib.sha256(data).hexdigest()
        key = f"objects/{content_hash}"

        # Check if already exists
        if not self._exists(key):
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
            print(f"Stored new content: {content_hash[:16]}...")
        else:
            print(f"Dedup: content already exists: {content_hash[:16]}...")

        return content_hash

    def _exists(self, key: str) -> bool:
        """Check if object exists."""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.s3.exceptions.ClientError:
            return False


# Deduplication in action
store = ContentStore(s3, "my-bucket")

# First upload
hash1 = store.store(b"Shared content")  # Stored

# Second upload of same content
hash2 = store.store(b"Shared content")  # Deduped! Not stored again

assert hash1 == hash2  # Same content, same hash
```

## Concept 3: Immutability

### What It Is

In CAS, content at a given address never changes. If content is different, it gets a different address. This provides strong guarantees about data consistency.

### Why It Matters

- **Safe caching**: Cache forever without invalidation
- **Reproducibility**: Same address = same content, always
- **Concurrent access**: No locks needed for reads
- **Audit trail**: Content can't be silently modified

### How It Works

```python
# Content at address is immutable
# If you "update" content, you get a NEW address

original = b"Version 1 content"
original_hash = store.store(original)

modified = b"Version 2 content"
modified_hash = store.store(modified)

# Different content = different hash
assert original_hash != modified_hash

# Original is still there, unchanged
retrieved = store.get(original_hash)
assert retrieved == original  # Still "Version 1 content"

# Both versions exist simultaneously
# Use external metadata to track "current" version
metadata = {
    "document_id": "doc-123",
    "current_version": modified_hash,
    "versions": [original_hash, modified_hash]
}
```

## Concept 4: Reference Counting

### What It Is

Reference counting tracks how many logical references point to a piece of content. This enables safe garbage collection in CAS systems.

### Why It Matters

- **Safe deletion**: Only delete when no references remain
- **Shared content**: Multiple files can share same chunks
- **Storage optimization**: Clean up orphaned content
- **Consistency**: Prevent premature deletion

### How It Works

```python
class RefCountedStore:
    """Content store with reference counting."""

    def __init__(self, s3_client, bucket: str, dynamodb_table):
        self.s3 = s3_client
        self.bucket = bucket
        self.refs = dynamodb_table

    def store_with_ref(self, data: bytes, ref_id: str) -> str:
        """Store content with a reference."""
        content_hash = hashlib.sha256(data).hexdigest()

        # Store content if new
        key = f"objects/{content_hash}"
        if not self._exists(key):
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)

        # Increment reference count
        self.refs.update_item(
            Key={"content_hash": content_hash},
            UpdateExpression="ADD ref_count :one, refs :ref_set",
            ExpressionAttributeValues={
                ":one": 1,
                ":ref_set": {ref_id}
            }
        )

        return content_hash

    def remove_ref(self, content_hash: str, ref_id: str) -> bool:
        """Remove a reference. Returns True if content was deleted."""
        # Decrement reference count
        response = self.refs.update_item(
            Key={"content_hash": content_hash},
            UpdateExpression="ADD ref_count :neg_one DELETE refs :ref_set",
            ExpressionAttributeValues={
                ":neg_one": -1,
                ":ref_set": {ref_id}
            },
            ReturnValues="ALL_NEW"
        )

        ref_count = response["Attributes"].get("ref_count", 0)

        # Delete content if no more references
        if ref_count <= 0:
            self.s3.delete_object(Bucket=self.bucket, Key=f"objects/{content_hash}")
            self.refs.delete_item(Key={"content_hash": content_hash})
            return True

        return False
```

## Concept 5: Chunking

### What It Is

Chunking breaks large files into smaller pieces, each stored with its own content address. This enables finer-grained deduplication and efficient transfers.

### Why It Matters

- **Better dedup**: Identical chunks across different files
- **Parallel operations**: Upload/download chunks concurrently
- **Resumable transfers**: Resume from last successful chunk
- **Partial updates**: Only transfer changed chunks

### How It Works

```python
class ChunkedStore:
    """Content store with chunk-based deduplication."""

    def __init__(self, s3_client, bucket: str, chunk_size: int = 1024 * 1024):
        self.s3 = s3_client
        self.bucket = bucket
        self.chunk_size = chunk_size

    def store_file(self, data: bytes) -> dict:
        """Store file as chunks, return manifest."""
        chunks = []

        # Split into chunks and store each
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunk_hash = self._store_chunk(chunk)
            chunks.append({
                "hash": chunk_hash,
                "offset": i,
                "size": len(chunk)
            })

        # Create manifest
        manifest = {
            "chunks": chunks,
            "total_size": len(data),
            "chunk_count": len(chunks)
        }

        # Store manifest itself
        manifest_data = json.dumps(manifest).encode()
        manifest_hash = self._store_chunk(manifest_data)

        return {"manifest_hash": manifest_hash, **manifest}

    def retrieve_file(self, manifest_hash: str) -> bytes:
        """Retrieve file from manifest."""
        # Get manifest
        manifest_data = self._get_chunk(manifest_hash)
        manifest = json.loads(manifest_data)

        # Reassemble chunks
        result = bytearray(manifest["total_size"])
        for chunk_info in manifest["chunks"]:
            chunk_data = self._get_chunk(chunk_info["hash"])
            offset = chunk_info["offset"]
            result[offset:offset + len(chunk_data)] = chunk_data

        return bytes(result)

    def _store_chunk(self, data: bytes) -> str:
        """Store a single chunk."""
        content_hash = hashlib.sha256(data).hexdigest()
        key = f"chunks/{content_hash}"

        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
        except:
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)

        return content_hash

    def _get_chunk(self, content_hash: str) -> bytes:
        """Retrieve a chunk by hash."""
        key = f"chunks/{content_hash}"
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()
```

## Concept 6: Integrity Verification

### What It Is

Verification ensures that retrieved content matches its expected hash, detecting corruption or tampering.

### Why It Matters

- **Data integrity**: Detect bit rot or corruption
- **Security**: Detect tampering
- **Trust**: Verify content from any source
- **Debugging**: Identify storage issues

### How It Works

```python
class VerifiedStore:
    """Content store with integrity verification."""

    def __init__(self, s3_client, bucket: str):
        self.s3 = s3_client
        self.bucket = bucket

    def get_verified(self, content_hash: str) -> bytes:
        """Retrieve content with integrity verification."""
        key = f"objects/{content_hash}"

        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = response["Body"].read()

        # Verify integrity
        actual_hash = hashlib.sha256(data).hexdigest()
        if actual_hash != content_hash:
            raise IntegrityError(
                f"Content integrity check failed: "
                f"expected {content_hash}, got {actual_hash}"
            )

        return data

    def verify_all(self) -> list[str]:
        """Verify all stored objects. Returns list of corrupted hashes."""
        corrupted = []

        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix="objects/"):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                expected_hash = key.split("/")[-1]

                try:
                    self.get_verified(expected_hash)
                except IntegrityError:
                    corrupted.append(expected_hash)

        return corrupted


class IntegrityError(Exception):
    """Raised when content doesn't match its hash."""
    pass
```

## Summary

Key takeaways from content-addressed storage:

1. **Hash-based addressing** provides unique, deterministic keys
2. **Automatic deduplication** reduces storage costs significantly
3. **Immutability** enables safe caching and concurrent access
4. **Reference counting** allows safe garbage collection
5. **Chunking** improves dedup ratio and enables partial operations
6. **Verification** ensures data integrity on retrieval
7. **CAS is foundational** for Git, Docker, IPFS, and modern backup systems

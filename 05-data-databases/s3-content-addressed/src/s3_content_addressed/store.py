"""Content-addressed storage implementation for S3.

Provides a high-level interface for storing and retrieving content
using hash-based addresses.
"""

from dataclasses import dataclass
from typing import Any

from botocore.exceptions import ClientError

from s3_content_addressed.hasher import compute_hash, verify_hash


class IntegrityError(Exception):
    """Raised when content doesn't match its expected hash."""

    pass


@dataclass
class StoreResult:
    """Result of a store operation."""

    content_hash: str
    size_bytes: int
    was_deduplicated: bool
    key: str


class ContentAddressedStore:
    """S3-backed content-addressed storage.

    Stores content using its SHA-256 hash as the key, providing
    automatic deduplication and integrity verification.
    """

    def __init__(
        self,
        s3_client: Any,
        bucket: str,
        prefix: str = "objects",
        algorithm: str = "sha256",
    ):
        """Initialize content-addressed store.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
            prefix: Key prefix for stored objects
            algorithm: Hash algorithm to use
        """
        self.s3 = s3_client
        self.bucket = bucket
        self.prefix = prefix
        self.algorithm = algorithm

    def store(self, data: bytes, metadata: dict[str, str] | None = None) -> StoreResult:
        """Store content and return its address.

        If content already exists, returns existing hash without re-uploading.

        Args:
            data: Content to store
            metadata: Optional S3 object metadata

        Returns:
            StoreResult with hash and dedup info
        """
        content_hash = compute_hash(data, self.algorithm)
        key = f"{self.prefix}/{content_hash}"

        # Check if already exists (deduplication)
        if self.exists(content_hash):
            return StoreResult(
                content_hash=content_hash,
                size_bytes=len(data),
                was_deduplicated=True,
                key=key,
            )

        # Upload to S3
        put_params: dict[str, Any] = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": data,
        }

        if metadata:
            put_params["Metadata"] = metadata

        self.s3.put_object(**put_params)

        return StoreResult(
            content_hash=content_hash,
            size_bytes=len(data),
            was_deduplicated=False,
            key=key,
        )

    def get(self, content_hash: str, verify: bool = True) -> bytes:
        """Retrieve content by its hash.

        Args:
            content_hash: Hash of content to retrieve
            verify: Whether to verify content integrity

        Returns:
            Content bytes

        Raises:
            IntegrityError: If verification fails
            ClientError: If object doesn't exist
        """
        key = f"{self.prefix}/{content_hash}"
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = response["Body"].read()

        if verify:
            if not verify_hash(data, content_hash, self.algorithm):
                raise IntegrityError(
                    f"Content integrity check failed for {content_hash}"
                )

        return data

    def exists(self, content_hash: str) -> bool:
        """Check if content exists.

        Args:
            content_hash: Hash to check

        Returns:
            True if content exists
        """
        key = f"{self.prefix}/{content_hash}"
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def delete(self, content_hash: str) -> bool:
        """Delete content by hash.

        Warning: In CAS systems, content may be shared. Use reference
        counting before deleting.

        Args:
            content_hash: Hash of content to delete

        Returns:
            True if deleted, False if didn't exist
        """
        if not self.exists(content_hash):
            return False

        key = f"{self.prefix}/{content_hash}"
        self.s3.delete_object(Bucket=self.bucket, Key=key)
        return True

    def list_objects(self, limit: int | None = None) -> list[str]:
        """List all content hashes in store.

        Args:
            limit: Maximum number of hashes to return

        Returns:
            List of content hashes
        """
        hashes = []
        paginator = self.s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket, Prefix=f"{self.prefix}/"):
            for obj in page.get("Contents", []):
                # Extract hash from key
                content_hash = obj["Key"].split("/")[-1]
                hashes.append(content_hash)

                if limit and len(hashes) >= limit:
                    return hashes

        return hashes

    def get_metadata(self, content_hash: str) -> dict[str, Any]:
        """Get object metadata.

        Args:
            content_hash: Hash of content

        Returns:
            Object metadata including size, last modified, etc.
        """
        key = f"{self.prefix}/{content_hash}"
        response = self.s3.head_object(Bucket=self.bucket, Key=key)

        return {
            "content_hash": content_hash,
            "size_bytes": response["ContentLength"],
            "last_modified": response["LastModified"],
            "etag": response["ETag"],
            "metadata": response.get("Metadata", {}),
        }

    def verify_integrity(self, content_hash: str) -> bool:
        """Verify stored content matches its hash.

        Args:
            content_hash: Hash to verify

        Returns:
            True if content matches hash
        """
        try:
            self.get(content_hash, verify=True)
            return True
        except IntegrityError:
            return False

    def copy_to(self, content_hash: str, dest_store: "ContentAddressedStore") -> bool:
        """Copy content to another store.

        Args:
            content_hash: Hash of content to copy
            dest_store: Destination store

        Returns:
            True if copied, False if already existed in destination
        """
        if dest_store.exists(content_hash):
            return False

        data = self.get(content_hash)
        dest_store.store(data)
        return True


class ChunkedStore:
    """Content store with chunk-based deduplication."""

    def __init__(
        self,
        s3_client: Any,
        bucket: str,
        chunk_size: int = 1024 * 1024,  # 1MB default
    ):
        """Initialize chunked store.

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
            chunk_size: Size of chunks in bytes
        """
        self.content_store = ContentAddressedStore(
            s3_client, bucket, prefix="chunks"
        )
        self.chunk_size = chunk_size

    def store_chunked(self, data: bytes) -> dict[str, Any]:
        """Store data in chunks.

        Args:
            data: Content to store

        Returns:
            Manifest with chunk hashes
        """
        chunks = []
        new_chunks = 0
        deduped_chunks = 0

        for i in range(0, len(data), self.chunk_size):
            chunk = data[i : i + self.chunk_size]
            result = self.content_store.store(chunk)

            chunks.append(
                {
                    "hash": result.content_hash,
                    "offset": i,
                    "size": len(chunk),
                }
            )

            if result.was_deduplicated:
                deduped_chunks += 1
            else:
                new_chunks += 1

        manifest = {
            "chunks": chunks,
            "total_size": len(data),
            "chunk_count": len(chunks),
            "new_chunks": new_chunks,
            "deduped_chunks": deduped_chunks,
        }

        # Store manifest itself
        import json

        manifest_data = json.dumps(manifest).encode()
        manifest_result = self.content_store.store(manifest_data)

        return {
            "manifest_hash": manifest_result.content_hash,
            **manifest,
        }

    def retrieve_chunked(self, manifest_hash: str) -> bytes:
        """Retrieve data from chunked manifest.

        Args:
            manifest_hash: Hash of the manifest

        Returns:
            Reassembled content
        """
        import json

        manifest_data = self.content_store.get(manifest_hash)
        manifest = json.loads(manifest_data)

        # Reassemble chunks
        result = bytearray(manifest["total_size"])

        for chunk_info in manifest["chunks"]:
            chunk_data = self.content_store.get(chunk_info["hash"])
            offset = chunk_info["offset"]
            result[offset : offset + len(chunk_data)] = chunk_data

        return bytes(result)
